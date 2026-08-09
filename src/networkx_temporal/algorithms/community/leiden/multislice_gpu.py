from typing import List, Optional, Union

from ....classes.types import is_static_graph, is_temporal_graph
from ....typing import StaticGraph, TemporalGraph
from ....utils.graph import to_supra_adjacency_matrix

_EPS = 1e-6
_BUDGET = 1 << 22


def leiden_multislice_gpu(
    graph: Union[TemporalGraph, StaticGraph],
    offsets: Optional[List[int]] = None,
    gamma: float = 1.0,
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    max_iter: int = 500,
    max_sweeps: int = 100,
    refine: bool = True,
    seed: Optional[int] = None,
) -> List[List[int]]:
    """ GPU-accelerated parallelized Leiden algorithm. Optimizes
    :func:`~networkx_temporal.algorithms.modularity_multislice` if ``graph`` is a
    :class:`~networkx_temporal.classes.TemporalGraph` object, or
    :func:`~networkx_temporal.algorithms.modularity` if ``graph`` is a static NetworkX graph
    object instead.

    Uses sparse `CuPy <https://cupy.dev/>`__ as a backend on single devices (AMD/NVIDIA).
    For multi-GPU or distributed computing, consider using the
    :func:`~networkx_temporal.algorithms.leiden_communities` function with ``device='gpu'``
    set, which uses `cuGraph <https://docs.rapids.ai/api/libcugraph/stable/>`__ as a backend
    (NVIDIA only), but optimizes global :func:`~networkx_temporal.algorithms.modularity` instead.

    Note that support for AMD GPUs (ROCm) is **experimental** and requires a `separate CuPy build
    <../examples/gpu.html#accelerating-temporal-graph-algorithms>`__.

    .. seealso::

        The `Examples → GPU acceleration → Compare running times
        <../examples/gpu.html#compare-running-times>`__
        and `Examples → GPU acceleration → Compare detection accuracy
        <../examples/gpu.html#compare-detection-accuracy>`__
        sections for efficiency/efficacy comparisons.

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param offsets: Optional list of node offsets for each slice. Allows passing a pre-computed
        supra-adjacency sparse CuPy matrix as ``graph``. If ``None``, construct supra-matrix.
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

    def one_hot(labels):
        """ Assignment matrix (n x n) with one unit entry per row. Wraps the
        per-level hoisted ``ones``/``indptr_n`` buffers, so a call allocates
        nothing; ``labels`` is aliased as the index array (read-only in SpGEMM).
        """
        return csp.csr_matrix((ones, labels, indptr_n), shape=(n, n))

    def volumes(labels, k):
        """ Per-label per-slice volume as a sparse ``(k, n_slices)`` matrix.
        Re-rows the degree matrix ``D`` through ``labels`` - via the per-level
        hoisted row map ``d_rows`` — and canonicalizes with a single COO->CSR
        sort, replacing the ``one_hot_T @ D`` SpGEMM plus its transpose/sort.
        ``_csr_keys`` and ``self_dot_scaled`` both assume sorted, deduplicated
        indices, so the canonicalization is required.
        """
        V = csp.coo_matrix((D.data, (labels[d_rows], D.indices)),
                           shape=(k, n_slices)).tocsr()
        V.sum_duplicates()
        V.sort_indices()
        return V

    def relabel(labels, bound):
        """ Relabel to a contiguous 0..k-1 range. Sort-free and sync-free:
        the label range is bounded by ``bound``, so a presence mask plus prefix
        sum replaces ``cp.unique``'s sort and its output-size host round-trip. """
        present = cp.zeros(bound, dtype=cp.int64)
        present[labels] = 1
        return (cp.cumsum(present) - 1)[labels]

    def self_dot_scaled(Ms, M, rows):
        """ Per-row inner product :math:`\\sum_t M_s[i, t] \\, M[i, t]` where ``Ms``
        is ``M`` with a per-column factor already folded in (shared sparsity).
        Replaces ``_row_dot`` for the self terms: pure elementwise product plus a
        segment sum, so no gather, no expansion, no budget chunking. ``rows`` is
        ``M``'s row expansion, passed pre-computed so it is shared with the other
        per-row kernels on the same matrix. Preserves the original per-entry
        product order (``Ms.data * M.data``, cast to float64). """
        out = cp.zeros(M.shape[0], dtype=cp.float64)
        if M.nnz == 0:
            return out
        cpx.scatter_add(out, rows, (Ms.data * M.data).astype(cp.float64))
        return out

    def drop_swaps(idx, source, dest, n_labels):
        """ Mask out reciprocal moves ``a -> b`` / ``b -> a``, keeping the one into
        the lower label. Synchronous moves would otherwise cycle forever. Plain
        ``sort`` instead of ``unique``: ``searchsorted`` tolerates duplicates, so
        the flag-and-compact passes are dropped. """
        if idx.shape[0] == 0:
            return idx
        keys = cp.sort(source * cp.int64(n_labels) + dest)
        reverse = dest * cp.int64(n_labels) + source
        pos = cp.clip(cp.searchsorted(keys, reverse), 0, keys.shape[0] - 1)
        return idx[~((keys[pos] == reverse) & (source > dest))]

    # Build supra-adjacency matrix on device...
    adj = graph
    if is_static_graph(graph) or is_temporal_graph(graph):
        adj, offsets = to_supra_adjacency_matrix(
            graph,
            weight=weight,
            interslice_weight=interslice_weight,
            return_offsets=True,
            device="gpu",
        )

    # ...or assume graph is already a sparse CuPy matrix.
    n_nodes = adj.shape[0]
    if offsets is None:
        offsets = [0]

    bounds = [int(o) for o in offsets]
    if not bounds or bounds[0] != 0:
        bounds = [0] + bounds
    if bounds[-1] != n_nodes:
        bounds = bounds + [n_nodes]
    n_slices = len(bounds) - 1

    # Slice membership, intra-slice degrees and per-slice, single-pass, deterministic.
    bounds_dev = cp.asarray(bounds, dtype=cp.int64)
    slice_of = cp.searchsorted(bounds_dev[1:], cp.arange(n_nodes, dtype=cp.int64),
                               side="right")

    # Per-nonzero slice id: slice boundaries in row space map to nonzero-space
    # boundaries through indptr, since rows are grouped by slice at level 0.
    nnz_bounds = adj.indptr[bounds_dev].astype(cp.int64)
    slice_of_nnz = cp.searchsorted(nnz_bounds[1:],
                                   cp.arange(adj.nnz, dtype=cp.int64),
                                   side="right")

    # Deterministic per-row reduction: the same cuSPARSE primitive the loop
    # used, applied once to the masked matrix instead of T times to submatrices.
    # ``masked`` aliases adj's index arrays; it is read-only and local.
    masked = csp.csr_matrix(
        (adj.data * (slice_of[adj.indices] == slice_of_nnz), adj.indices, adj.indptr),
        shape=adj.shape)
    degree = cp.asarray(masked.sum(axis=1)).ravel().astype(cp.float32)

    # Deterministic per-slice totals: slices are contiguous, so a float64
    # prefix sum differenced at the bounds replaces T separate reductions
    # (and is more accurate than float32 per-slice sums at large m_t).
    cs = cp.concatenate((cp.zeros(1, cp.float64),
                         cp.cumsum(degree, dtype=cp.float64)))
    denom = cp.maximum(cs[bounds_dev[1:]] - cs[bounds_dev[:-1]],
                       1e-12).astype(cp.float32)  # 2*m_t

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
        # Per-level buffers shared by every one_hot()/volumes() call: the
        # assignment-matrix values and indptr, and D's row expansion.
        ones = cp.ones(n, adj.dtype)
        indptr_n = cp.arange(n + 1, dtype=cp.int64)
        d_rows = cp.repeat(cp.arange(D.shape[0], dtype=cp.int64),
                           cp.diff(D.indptr).astype(cp.int64))
        Dc = _scale_cols(D, coef)                 # gamma/(2*m_t) folded at once.

        # One entry per row holds at level 0, where every supra-node lives in a
        # single slice; hoisted so the fast-path in _row_dot does not cost a
        # device sync on every sweep.
        simple = D.nnz == D.shape[0] and bool((cp.diff(D.indptr) == 1).all())
        self_null = self_dot_scaled(Dc, D, d_rows)  # sum_t Dc[i,t] * D[i,t].

        # Local moving phase, parallelized on the GPU. Labels are kept in
        # [0, n) without relabeling between sweeps (targets are existing labels),
        # so the per-sweep comm.max() sync and relabel are both gone; the
        # canonical relabel only has to happen once at aggregation.
        converged = False
        for _move in range(max_sweeps):
            P = one_hot(comm)
            volume = volumes(comm, n)
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

            # At most one own pair per node in a canonical product, so a plain
            # (non-atomic) scatter assignment replaces scatter_add.
            stay[node[own]] = gain[own]

            # Single convergence sync: drop_swaps handles the empty case, so
            # movers.shape[0] alone decides the break.
            moving = cp.nonzero(
                (target >= 0) & (target != comm) & (best > stay + _EPS))[0]
            movers = drop_swaps(moving, comm[moving], target[moving], n)
            if movers.shape[0] == 0:
                converged = True
                break
            comm[movers] = target[movers]

        # Refinement phase, parallelized on the GPU.
        if refine:
            if converged:
                # Reuse the last move sweep's supra product when the loop converged:
                # comm is unchanged since it was computed, so volume/keys/(node,cand,own)
                # and the mutated conn (= raw - own*diag) are exactly refinement's
                # community-level inputs. Only max_sweeps exhaustion needs a recompute.
                vol_comm, keys_comm = volume, keys_vol
                rn, rc, rconn, rown = node, cand, conn, own
            else:
                P = one_hot(comm)
                vol_comm = volumes(comm, n)
                keys_comm = _csr_keys(vol_comm, n_slices)
                rn, rc, raw = _spgemm_coo(adj, P)
                rown = rc == comm[rn]
                rconn = raw - rown * diag[rn]

            conn_comm = cp.zeros(n, dtype=cp.float32)
            conn_comm[rn[rown]] = rconn[rown]  # One own pair per node; no atomics.

            # Check if each node is well-connected to the rest of its community.
            node_ok = (conn_comm - (
                _row_dot(Dc, vol_comm, keys_comm, idx, comm, n_slices, simple) - self_null
            )) >= -_EPS

            # Partitions only ever absorb singletons from their own community,
            # so the live-label -> community map is comm itself throughout the
            # loop; emptied labels are only ever read through empty vol_sub rows
            # (contributing zero) and never appear as candidates.
            part = cp.arange(n, dtype=cp.int64)
            for _refine in range(max_sweeps):
                P_sub = one_hot(part)
                vol_sub = volumes(part, n)
                sub_rows = cp.repeat(cp.arange(n, dtype=cp.int64),
                                     cp.diff(vol_sub.indptr).astype(cp.int64))
                keys_sub = _csr_keys(vol_sub, n_slices, sub_rows)
                vol_sub_c = _scale_cols(vol_sub, coef)
                size = cp.bincount(part, minlength=n)

                node, cand, conn = _spgemm_coo(adj, P_sub)

                # Check if subcommunity is well-connected to the rest of its community.
                internal = cp.zeros(n, dtype=cp.float32)
                own_sub = cand == part[node]
                cpx.scatter_add(internal, cand[own_sub], conn[own_sub])
                total = cp.zeros(n, dtype=cp.float32)
                cpx.scatter_add(total, part[node], conn)
                sub_ok = ((total - internal) - (
                    _row_dot(vol_sub_c, vol_comm, keys_comm, idx, comm, n_slices, False)
                    - self_dot_scaled(vol_sub_c, vol_sub, sub_rows)
                )) >= -_EPS

                # Only singleton, well-connected nodes merge along an edge,
                # within their community, into a well-connected target.
                eligible = (node_ok & (size[part] == 1))[node] \
                    & (comm[cand] == comm[node]) \
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

                moving = cp.nonzero(target >= 0)[0]
                movers = drop_swaps(moving, part[moving], target[moving], n)
                if movers.shape[0] == 0:
                    break
                part[movers] = target[movers]
            part = relabel(part, n)
        else:
            comm = relabel(comm, n)
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
        D = volumes(part, n_parts)
        compose = part[compose]
        comm = relabel(seed_part, n)

    labels = cp.asnumpy(relabel(comm[compose], comm.shape[0])).astype(int).tolist()
    return [labels[start:end] for start, end in zip(bounds, bounds[1:])]


def _spgemm_coo(adj, X):
    """ Node-to-group connection triples of ``adj @ X`` as ``(row, col, data)``.

    Single call site for the sparse product that dominates every sweep. Kept
    separate so a future distributed backend is a substitution rather than a
    rewrite of the move and refinement phases. NOTE: A sort-based reduce over
    relabeled columns (``sum_duplicates``) is a candidate replacement here.
    """
    S = (adj @ X).tocoo()
    return S.row, S.col, S.data


def _csr_keys(M, n_cols, rows=None):
    """ Globally sorted ``row * n_cols + col`` coordinate keys of a CSR matrix.

    Valid only for canonical CSR (indices sorted within each row, no duplicates),
    which makes random access by coordinate a single binary search. Callers must
    have run ``sum_duplicates`` and ``sort_indices`` on any SpGEMM output first;
    an unsorted matrix yields wrong values rather than an error; ``rows`` may be
    passed pre-computed to share row expansion with other matrix per-row kernels.
    """
    import cupy as cp
    if rows is None:
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

    ``one_per_row`` is passed explicitly at every call site to avoid the
    ``(diff(indptr) == 1).all()`` device sync; the ``None`` auto-detect is kept
    only as a fallback and short-circuits host-side on ``nnz != n_rows``.
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
