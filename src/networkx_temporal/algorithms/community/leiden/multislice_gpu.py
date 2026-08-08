from typing import List, Optional, Union

from ....typing import StaticGraph, TemporalGraph
from ....utils.graph import to_supra_adjacency_matrix

_EPS = 1e-6
_BUDGET = 1 << 22


def leiden_multislice_gpu(
    graph: Union[TemporalGraph, StaticGraph],
    gamma: float = 1.0,
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    max_iter: int = 500,
    max_sweeps: int = 100,
    refine: bool = True,
    seed: Optional[int] = None,
) -> List[List[int]]:
    """ GPU-accelerated parallelized Leiden algorithm. Optimizes
    :func:`~networkx_temporal.algorithms.modularity_multislice`.

    Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a static NetworkX graph, or a list
    of static NetworkX graphs as input. Uses sparse `CuPy <https://cupy.dev/>`__ as a backend on
    single devices (AMD/NVIDIA). For multi-GPU or distributed computing, consider using the
    :func:`~networkx_temporal.algorithms.leiden_communities` function with ``device='gpu'``
    set, which uses `cuGraph <https://docs.rapids.ai/api/libcugraph/stable/>`__ as a backend
    (NVIDIA only), which optimizes global :func:`~networkx_temporal.algorithms.modularity` instead.

    .. seealso::

        The `Examples → GPU acceleration → Compare running times
        <../examples/gpu.html#compare-running-times>`__
        and `Examples → GPU acceleration → Compare detection accuracy
        <../examples/gpu.html#compare-detection-accuracy>`__
        sections for efficiency/efficacy comparisons.

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param gamma: Resolution parameter :math:`\\gamma` (default: ``1.0``).
        Controls the size of communities, where higher values lead to smaller communities.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
        Only sequental slices are coupled.
    :param max_iter: Maximum coarsening levels. Default: ``500``.
    :param max_sweeps: Maximum sweeps per phase, per iteration. Default: ``100``.
        Used for parallelized local moving and refinement phases.
    :param refine: Whether to run the refinement phase of Leiden. Default is ``True``.
        If ``False``, yields a Louvain-like algorithm that is slightly faster.
    :param seed: Random seed number for reproducibility. Note that parallelized GPU computations
        may not be fully deterministic across runs.
    """
    try:
        import cupy as cp
        import cupyx as cpx
        import cupyx.scipy.sparse as csp
    except ImportError as exc:
        raise ImportError(
            "GPU multislice Leiden requires cupy. Please install it via "
            "`conda install -c conda-forge -c rapidsai -c nvidia cupy`."
        ) from exc

    if seed is not None:
        cp.random.seed(seed)

    def one_hot(labels, n, k, dtype):
        """ Assignment matrix (n x k) with one unit entry per row."""
        return csp.csr_matrix(
            (cp.ones(n, dtype), labels, cp.arange(n + 1, dtype=cp.int64)),
            shape=(n, k),
        )

    def one_hot_T(labels, n, k, dtype):
        """ Transposed assignment matrix (k x n). A stable sort groups rows by
        label while leaving node ids ascending within each group, so the result
        is canonical CSR without a further sort. """
        return one_hot(labels, n, k, dtype).T.tocsr()
        # order = cp.argsort(labels, kind="stable").astype(cp.int64)
        # indptr = cp.concatenate([
        #     cp.zeros(1, dtype=cp.int64),
        #     cp.cumsum(cp.bincount(labels, minlength=k).astype(cp.int64)),
        # ])
        # return csp.csr_matrix((cp.ones(n, dtype), order, indptr), shape=(k, n))

    def volumes(labels, n, k):
        """ Per-label per-slice volume as a sparse ``(k, n_slices)`` matrix.
        Replaces a ``scatter_add`` into a dense ``(k, n_slices)`` buffer. The
        canonicalization is required: ``_csr_keys`` assumes sorted, deduplicated
        indices and SpGEMM guarantees neither.
        """
        V = (one_hot_T(labels, n, k, D.dtype) @ D).tocsr()
        V.sum_duplicates()
        V.sort_indices()
        return V

    def relabel(labels):
        """ Relabel to a contiguous 0..k-1 range."""
        return cp.unique(labels, return_inverse=True)[1].astype(cp.int64).ravel()

    def drop_swaps(moving, source, dest, n_labels):
        """ Mask out reciprocal moves ``a -> b`` / ``b -> a``, keeping the one into
        the lower label. Synchronous moves would otherwise cycle forever. """
        keys = cp.unique(source * cp.int64(n_labels) + dest)
        reverse = dest * cp.int64(n_labels) + source
        pos = cp.clip(cp.searchsorted(keys, reverse), 0, keys.shape[0] - 1)
        return cp.nonzero(moving)[0][~((keys[pos] == reverse) & (source > dest))]

    # Build supra-adjacency matrix on device.
    adj, offsets = to_supra_adjacency_matrix(
        graph,
        weight=weight,
        interslice_weight=interslice_weight,
        return_offsets=True,
        device="gpu",
    )
    n_nodes = adj.shape[0]

    # Intra-slice degrees, per-slice 2*m_t.
    bounds = [int(o) for o in offsets]
    if not bounds or bounds[0] != 0:
        bounds = [0] + bounds
    if bounds[-1] != n_nodes:
        bounds = bounds + [n_nodes]
    n_slices = len(bounds) - 1

    slice_of = cp.zeros(n_nodes, dtype=cp.int64)
    degree = cp.zeros(n_nodes, dtype=cp.float32)
    denom = cp.zeros(n_slices, dtype=cp.float32)
    for t in range(n_slices):
        start, end = bounds[t], bounds[t + 1]
        slice_of[start:end] = t
        d_t = cp.asarray(adj[start:end, start:end].sum(axis=1)).ravel()
        degree[start:end] = d_t
        denom[t] = cp.maximum(d_t.sum(), 1e-12)   # 2*m_t

    # D[i, t] = intra-slice degree of node i in slice t (absent if not present).
    # Exactly one entry per row at level 0; aggregation takes unions of member
    # rows, so the nonzero count never grows.
    D = csp.csr_matrix(
        (degree, slice_of, cp.arange(n_nodes + 1, dtype=cp.int64)),
        shape=(n_nodes, n_slices))
    coef = cp.float32(gamma) / denom              # gamma / (2*m_t)

    compose = cp.arange(n_nodes, dtype=cp.int64)  # Original node -> super-node.
    comm = cp.arange(n_nodes, dtype=cp.int64)     # Community of each super-node.

    for _iter in range(max_iter):
        n = adj.shape[0]
        diag = adj.diagonal()                     # Self-loop contributions.

        idx = cp.arange(n, dtype=cp.int64)
        Dc = _scale_cols(D, coef)                 # gamma/(2*m_t) folded at once.
        keys_D = _csr_keys(D, n_slices)

        # One entry per row holds at level 0, where every supra-node lives in a # single slice;
        # hoisted so the fast-path in _row_dot so it does not cost a device sync on every sweep.
        simple = D.nnz == D.shape[0] and bool((cp.diff(D.indptr) == 1).all())
        self_null = _row_dot(Dc, D, keys_D, idx, idx, n_slices, simple)

        # Local moving phase, parallelized on the GPU.
        for _move in range(max_sweeps):
            n_comms = int(comm.max()) + 1
            P = one_hot(comm, n, n_comms, adj.dtype)
            volume = volumes(comm, n, n_comms)
            keys_vol = _csr_keys(volume, n_slices)

            node, cand, conn = _spgemm_coo(adj, P)
            own = cand == comm[node]
            conn = conn - own * diag[node]  # Remove self-loop contributions.

            null = _row_dot(Dc, volume, keys_vol, node, cand, n_slices, simple)
            null = null - own * self_null[node]
            gain = conn - null

            best = cp.full(n, -cp.inf, dtype=cp.float64)
            cpx.scatter_max(best, node, gain)
            target = cp.full(n, -1, dtype=cp.int64)
            winner = gain >= best[node] - _EPS
            target[node[winner]] = cand[winner]

            stay = cp.zeros(n, dtype=cp.float64)  # Gain of not moving.
            cpx.scatter_add(stay, node[own], gain[own])

            moving = (target >= 0) & (target != comm) & (best > stay + _EPS)
            if not bool(moving.any()):
                break
            movers = drop_swaps(moving, comm[moving], target[moving], n_comms)
            if movers.shape[0] == 0:
                break
            comm[movers] = target[movers]
            comm = relabel(comm)

        comm = relabel(comm)

        # Refinement phase, parallelized on the GPU.
        if refine:
            n_comms = int(comm.max()) + 1
            P = one_hot(comm, n, n_comms, adj.dtype)
            vol_comm = volumes(comm, n, n_comms)
            keys_comm = _csr_keys(vol_comm, n_slices)

            # Check if each node is well-connected to the rest of its community.
            srow, scol, sdata = _spgemm_coo(adj, P)
            inside = scol == comm[srow]
            conn_comm = cp.zeros(n, dtype=cp.float32)
            cpx.scatter_add(conn_comm, srow[inside], sdata[inside])
            conn_comm = conn_comm - diag
            node_ok = (conn_comm - (
                _row_dot(Dc, vol_comm, keys_comm, idx, comm, n_slices, simple) - self_null
            )) >= -_EPS

            part = cp.arange(n, dtype=cp.int64)
            for _refine in range(max_sweeps):
                n_subs = int(part.max()) + 1
                P_sub = one_hot(part, n, n_subs, adj.dtype)
                vol_sub = volumes(part, n, n_subs)
                keys_sub = _csr_keys(vol_sub, n_slices)
                vol_sub_c = _scale_cols(vol_sub, coef)
                sub_idx = cp.arange(n_subs, dtype=cp.int64)
                size = cp.bincount(part, minlength=n_subs)
                comm_of_sub = cp.zeros(n_subs, dtype=cp.int64)
                comm_of_sub[part] = comm

                node, cand, conn = _spgemm_coo(adj, P_sub)

                # Check if subcommunity is well-connected to the rest of its community.
                internal = cp.zeros(n_subs, dtype=cp.float32)
                own_sub = cand == part[node]
                cpx.scatter_add(internal, cand[own_sub], conn[own_sub])
                total = cp.zeros(n_subs, dtype=cp.float32)
                cpx.scatter_add(total, part[node], conn)
                sub_ok = ((total - internal) - (
                    _row_dot(vol_sub_c, vol_comm, keys_comm,
                             sub_idx, comm_of_sub, n_slices)
                    - _row_dot(vol_sub_c, vol_sub, keys_sub,
                               sub_idx, sub_idx, n_slices)
                )) >= -_EPS

                # Only singleton, well-connected nodes merge along an edge,
                # within their community, into a well-connected target.
                eligible = (node_ok & (size[part] == 1))[node] \
                    & (comm_of_sub[cand] == comm[node]) \
                    & (cand != part[node]) & sub_ok[cand] & (conn > 0)
                if not bool(eligible.any()):
                    break
                node, cand, conn = node[eligible], cand[eligible], conn[eligible]
                gain = conn - _row_dot(Dc, vol_sub, keys_sub, node, cand, n_slices, simple)
                positive = gain >= -_EPS
                if not bool(positive.any()):
                    break
                node, cand, gain = node[positive], cand[positive], gain[positive]

                best = cp.full(n, -cp.inf, dtype=cp.float64)
                cpx.scatter_max(best, node, gain)
                target = cp.full(n, -1, dtype=cp.int64)
                winner = gain >= best[node] - _EPS
                target[node[winner]] = cand[winner]

                moving = target >= 0
                if not bool(moving.any()):
                    break
                movers = drop_swaps(moving, part[moving], target[moving], n_subs)
                if movers.shape[0] == 0:
                    break
                part[movers] = target[movers]
                part = relabel(part)
            part = relabel(part)
        else:
            part = comm.copy()

        n_parts = int(part.max()) + 1
        if n_parts == n:
            break

        # Aggregate (contract by reduce_by_key) the refined partition,
        # the next level's communities from the non-refined one.
        seed_part = cp.zeros(n_parts, dtype=cp.int64)
        seed_part[part] = comm
        coo = adj.tocoo()
        adj = csp.coo_matrix(
            (coo.data, (part[coo.row], part[coo.col])), shape=(n_parts, n_parts)).tocsr()

        # Update the per-slice null model for the next level.
        D = volumes(part, n, n_parts)
        compose = part[compose]
        comm = relabel(seed_part)

    labels = cp.asnumpy(relabel(comm[compose])).astype(int).tolist()
    return [labels[start:end] for start, end in zip(bounds, bounds[1:])]


def _spgemm_coo(adj, X):
    """ Node-to-group connection triples of ``adj @ X`` as ``(row, col, data)``.
    Single call site for the sparse product that dominates every sweep. Kept
    separate so a future distributed backend is a substitution rather than a
    rewrite of the move and refinement phases.
    """
    S = (adj @ X).tocoo()
    return S.row, S.col, S.data


def _csr_keys(M, n_cols):
    """ Globally sorted ``row * n_cols + col`` coordinate keys of a CSR matrix.
    Valid only for canonical CSR (indices sorted within each row, no duplicates),
    which makes random access by coordinate a single binary search. Callers must
    have run ``sum_duplicates`` and ``sort_indices`` on any SpGEMM output first;
    an unsorted matrix yields wrong values rather than an error.
    """
    import cupy as cp
    rows = cp.repeat(cp.arange(M.shape[0], dtype=cp.int64),
                     cp.diff(M.indptr).astype(cp.int64))
    return rows * cp.int64(n_cols) + M.indices.astype(cp.int64)


def _gather(keys, data, query):
    """ ``M[row, col]`` for coordinate keys, zero where the entry is absent."""
    import cupy as cp
    if keys.shape[0] == 0:
        return cp.zeros(query.shape[0], dtype=data.dtype)
    pos = cp.clip(cp.searchsorted(keys, query), 0, keys.shape[0] - 1)
    return cp.where(keys[pos] == query, data[pos], data.dtype.type(0))


def _row_dot(A, B, keys_B, rows_a, rows_b, n_cols, one_per_row=None):
    """ Per-pair sparse row inner product :math:`\\sum_t A[a_e, t] \\, B[b_e, t]`.

    Cap on the expansion buffer of a single ``_row_dot`` block in entries by _BUDGET.
    The sampled product expands over one factor's nonzeros, so an unchunked call
    transiently allocates up to ``n_slices * nnz(adj @ P)`` — measurably several
    times the connection matrix itself once coarsening makes the degree matrix
    multi-slice. Chunking bounds that at a fixed cost in host round-trips
    (``expansion / _BUDGET`` per call, single digits in practice).
    """
    import cupy as cp
    import cupyx as cpx
    m = rows_a.shape[0]
    out = cp.zeros(m, dtype=cp.float64)
    if m == 0 or A.nnz == 0 or B.nnz == 0:
        return out

    # Fast path: exactly one nonzero per row (the level-0 degree matrix). Pure
    # gather, no expansion and no reduction, so no chunking is needed either.
    if one_per_row is None:
        one_per_row = A.nnz == A.shape[0] and bool((cp.diff(A.indptr) == 1).all())
    if one_per_row:
        cols = A.indices.astype(cp.int64)[rows_a]
        return (A.data[rows_a] * _gather(
            keys_B, B.data, rows_b * cp.int64(n_cols) + cols)).astype(cp.float64)

    indptr = A.indptr.astype(cp.int64)
    counts = cp.diff(indptr)[rows_a]
    ends = cp.cumsum(counts)
    total = int(ends[-1])
    if total == 0:
        return out

    lo, base = 0, 0
    while lo < m:
        if total - base <= _BUDGET:
            # Common case: no second sync.
            hi, blk_total = m, total - base
        else:
            # Largest block whose expansion stays within budget; at least one pair.
            hi = max(int(cp.searchsorted(ends, base + _BUDGET, side="right")), lo + 1)
            blk_total = int(ends[hi - 1]) - base
        blk_counts = counts[lo:hi]

        # Ragged range: for each pair e, walk the nonzeros of row rows_a[e].
        e = cp.repeat(cp.arange(lo, hi, dtype=cp.int64), blk_counts)
        head = cp.repeat(cp.cumsum(blk_counts) - blk_counts, blk_counts)
        pos = cp.repeat(indptr[rows_a[lo:hi]], blk_counts) \
            + (cp.arange(blk_total, dtype=cp.int64) - head)
        cols = A.indices[pos].astype(cp.int64)

        cpx.scatter_add(out, e, (A.data[pos] * _gather(
            keys_B, B.data, rows_b[e] * cp.int64(n_cols) + cols)).astype(cp.float64))
        lo, base = hi, base + blk_total
    return out


def _scale_cols(M, coef):
    """ Folds a per-column factor into a CSR matrix's values."""
    out = M.copy()
    out.data = out.data * coef[M.indices]
    return out
