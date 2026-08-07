from typing import List, Optional, Tuple, Union

import networkx as nx
import numpy as np
import scipy.sparse as sp
from networkx import NetworkXError

from ..classes.functions import from_multigraph
from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import Literal, StaticGraph, TemporalGraph

FORMAT = Literal["csr", "csc", "dok", "lil"]
FORMATS = list(FORMAT.__args__)


def combine_snapshots(graphs: List[TemporalGraph]) -> TemporalGraph:
    """ Returns temporal graph with combined snapshots.

    Each snapshot in the resulting temporal graph is the union of the corresponding
    snapshots at each index :math:`t` from ``graphs``. All input temporal graphs
    must have the same number of snapshots.

    .. seealso::

        The `Examples → Basic operations → Combine snapshots
        <../examples/basics.html#combine-snapshots>`__  page for an example.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG1 = tx.temporal_graph()
        >>> TG2 = tx.temporal_graph()
        >>>
        >>> TG1.add_edge("a", "b")
        >>> TG2.add_edge("c", "b")
        >>>
        >>> TG = tx.combine_snapshots([TG1, TG2])
        >>> print(TG)

        TemporalGraph with 1 snapshots and 3 nodes and 2 edges

    :param object graphs: A list of :class:`~networkx_temporal.classes.TemporalGraph`
        objects.
    """
    if len(graphs) == 0:
        raise ValueError("Argument `graphs` must contain at least one graph.")

    graph = next(iter(graphs))  # Get the first graph to check type and number of snapshots.

    temporal = all(is_temporal_graph(TG) for TG in graphs)
    if not temporal:
        raise NetworkXError("All inputs must be temporal NetworkX graphs.")

    multigraph = all(TG.is_multigraph() == graph.is_multigraph() for TG in graphs)
    if not multigraph:
        raise NetworkXError("All inputs must be either multigraph or non-multigraph objects.")

    if any(len(TG) != len(graph) for TG in graphs):
        raise ValueError("All temporal graphs must have the same number of snapshots.")

    # Initialize empty temporal graph of the same type.
    TG = graph.__class__(t=0)

    # Add snapshots as unions of corresponding snapshots from each graph.
    TG.add_snapshots_from([
        nx.compose_all([g[t] for g in graphs])
        for t in range(len(graph))
    ])
    TG.index = graph.index
    return TG


def propagate_snapshots(
    TG: TemporalGraph,
    method: Literal["ffill", "bfill"] = "ffill",
    delta: Optional[int] = None,
) -> TemporalGraph:
    """ Propagates nodes and edges across snapshots.

    Returns a temporal graph where nodes and edges are preserved
    among snapshots.

    .. seealso::

        The `Examples → Basic operations → Propagate snapshots
        <../examples/basics.html#propagate-snapshots>`__  page for an example.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param str method: The propagation method. Can be either:

       - ``'ffill'``: propagates nodes and edges forward in time
         (from earlier to later snapshots);

       - ``'bfill'``: propagates nodes and edges backward in time
         (from later to earlier snapshots).
    :param delta: The number of snapshots to propagate over.
        If ``None`` (default), propagates over all snapshots.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")
    if method not in ("ffill", "bfill"):
        raise ValueError("Argument `method` must be one of ('ffill', 'bfill').")

    TG = TG.copy()

    if method == "ffill":
        for t in range(1, len(TG)):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(max(0, t - delta if delta is not None else 0), t + 1)
            ])
    else:  # method == "bfill"
        for t in range(len(TG)-2, -1, -1):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(t, min(len(TG), t + (delta if delta is not None else len(TG))))
            ])

    return TG


def to_adjacency_matrix(
    graph: Union[TemporalGraph, StaticGraph],
    weight: Optional[str] = "weight",
    device: Literal["cpu", "gpu"] = "cpu",
    dtype: Optional[object] = None,
    format: FORMAT = "csr",
) -> sp.spmatrix:
    """ Returns sparse adjacency matrix of graph.

    If ``graph`` is a :class:`~networkx_temporal.classes.TemporalGraph`, returns a single weighted
    adjacency matrix combining all snapshots; if a static
    :class:`~networkx_temporal.typing.StaticGraph`, returns a single adjacency matrix.

    .. note::

        Supports CPU and GPU computation with SciPy and CuPy, by setting ``device='cpu'`` (default)
        or ``device='gpu'``, respectively. The resulting matrix can be made dense with ``.todense()``.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.example_sbm_graph()
        >>> TG = TG.subgraph([0, 1, 2]).copy()
        >>> TG.remove_nodes_from(tx.isolates(TG))
        >>>
        >>> for t, G in enumerate(TG):
        >>>     print(f"Snapshot {t}:")
        >>>     print(f"- Nodes: {list(G.nodes())}")
        >>>     print(f"- Edges: {list(G.edges())}")
        >>>
        >>> A = tx.to_adjacency_matrix(TG)
        >>> A.todense()

        Snapshot 0:
        - Nodes: [0, 1, 2]
        - Edges: [(0, 1), (0, 2)]
        Snapshot 1:
        - Nodes: [1, 2]
        - Edges: [(1, 2)]
        Snapshot 2:
        - Nodes: [0, 2]
        - Edges: [(0, 2)]

        matrix([[0., 1., 2.],
                [1., 0., 1.],
                [2., 1., 0.]], dtype=float32)

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
            object.
    :param weight: Edge attribute name to use as weight.
        ``None`` treats all weights as 1. Default: ``'weight'``.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy and SciPy (default).

        - ``'gpu'``: Uses CuPy and CuPy sparse.

    :param dtype: Data type for the resulting sparse matrix values.
        If unset, uses NumPy ``float32`` (CPU) or CuPy ``float32`` (GPU).
    :param str format: Sparse matrix format. Available choices:

        - ``'csr'``: Compressed Sparse Row (default).

        - ``'csc'``: Compressed Sparse Column.

        - ``'dok'``: Dictionary of Keys (CPU only).

        - ``'lil'``: List of Lists (CPU only).

    """
    if is_temporal_graph(graph):
        graph = from_multigraph(graph).flatten()
    elif not is_static_graph(graph):
        raise TypeError("Argument `graph` must be a temporal or static NetworkX graph.")
    return to_supra_adjacency_matrix(
        graph,
        weight=weight,
        device=device,
        dtype=dtype,
        format=format,
    )


def to_supra_adjacency_matrix(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    interslice_weights: Optional[dict[tuple[int, int], float]] = None,
    interslice_couple: Literal["all", "first", "shared"] = "shared",
    interslice_directed: bool = False,
    return_offsets: bool = False,
    device: Literal["cpu", "gpu"] = "cpu",
    dtype: Optional[object] = None,
    format: FORMAT = "csr",
) -> Union[sp.spmatrix, Tuple[sp.spmatrix, List[int]]]:
    """ Returns sparse supra-adjacency matrix of temporal graph.

    The supra-adjacency matrix is a block matrix with intra-slice adjacency matrices on the
    diagonal and inter-slice identity matrices on the off-diagonal blocks, representing
    inter-slice couplings:

    .. math::

        \\mathbf{A}^\\mathrm{supra} =
        \\left(
        \\begin{array}{cccc}
            \\mathbf{A}^{(1)} & \\omega \\mathbf{I} & \\cdots & \\mathbf{0} \\\\
            \\omega \\mathbf{I} & \\mathbf{A}^{(2)} & \\cdots & \\mathbf{0} \\\\
            \\vdots & \\vdots & \\ddots & \\vdots \\\\
            \\mathbf{0} & \\mathbf{0} & \\cdots & \\mathbf{A}^{(T)}
        \\end{array}
        \\right).

    It is possible to configure ``interslice_couple`` to connect only ``'shared'``
    nodes present in sequential snapshots, i.e., :math:`t` and :math:`t+1` (default);
    ``'all'`` temporal node copies across every snapshot; or only the ``'first'`` occurrence of
    each node in a subsequent snapshot.

    Inter-slice couplings are symmetric (undirected) by default; if ``interslice_directed=True``,
    the resulting supra-adjacency matrix is asymmetric (directed) with couplings from earlier to
    later snapshots. A constant ``interslice_weight`` (default: 1.0) is applied to all couplings,
    optionally overriden by an ``interslice_weights`` dictionary with snapshot tuples as keys.
    If ``interslice_weight=0``, no inter-slice couplings are added. If the graph is a multigraph,
    the resulting matrix is weighted by the sum of edge weights among nodes in each snapshot.

    Setting ``return_offsets=True`` returns a tuple of the supra-adjacency matrix and a list of
    starting indices for each slice, to be used with specialized algorithms for temporal graphs.

    .. note::

        Supports CPU and GPU computation with SciPy and CuPy, by setting ``device='cpu'`` (default)
        or ``device='gpu'``, respectively. The resulting matrix can be made dense with ``.todense()``.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.example_sbm_graph()
        >>> TG = TG.subgraph([0, 1, 2]).copy()
        >>> TG.remove_nodes_from(tx.isolates(TG))
        >>>
        >>> for t, G in enumerate(TG):
        >>>     print(f"Snapshot {t}:")
        >>>     print(f"- Nodes: {list(G.nodes())}")
        >>>     print(f"- Edges: {list(G.edges())}")
        >>>
        >>> A = tx.to_supra_adjacency_matrix(TG)
        >>> A.todense()

        Snapshot 0:
        - Nodes: [0, 1, 2]
        - Edges: [(0, 1), (0, 2)]
        Snapshot 1:
        - Nodes: [1, 2]
        - Edges: [(1, 2)]
        Snapshot 2:
        - Nodes: [0, 2]
        - Edges: [(0, 2)]

        matrix([[0., 1., 1., 0., 0., 0., 0.],
                [1., 0., 0., 1., 0., 0., 0.],
                [1., 0., 0., 0., 1., 0., 0.],
                [0., 0., 0., 0., 1., 0., 0.],
                [0., 0., 0., 1., 0., 0., 1.],
                [0., 0., 0., 0., 0., 0., 1.],
                [0., 0., 0., 0., 0., 1., 0.]], dtype=float32)

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
    :param interslice_weights: A dictionary mapping inter-slice layer tuples to weights, e.g.,
        ``{(0, 1): 1, (0, 2): 0.5}``. Overrides only defined snapshot tuples if provided. Optional.
    :param interslice_couple: Inter-slice coupling type. Default: ``'shared'``.
        Available choices:

        - ``'all'``: Connects all nodes across snapshots.

        - ``'first'``: Connects each node to its first occurrence in the next snapshot.

        - ``'shared'``: Connects only nodes that are present in both snapshots.

    :param interslice_directed: If ``True``, inter-slice couplings are unidirectional (from earlier
        to later snapshots). If ``False``, inter-slice couplings are bidirectional (default).
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy and SciPy (default).

        - ``'gpu'``: Uses CuPy and CuPy sparse.

    :param dtype: Data type for the resulting sparse matrix values.
        If unset, uses NumPy ``float32`` (CPU) or CuPy ``float32`` (GPU).
    :param str format: Sparse matrix format. Available choices:

        - ``'csr'``: Compressed Sparse Row (default).

        - ``'csc'``: Compressed Sparse Column.

        - ``'dok'``: Dictionary of Keys (CPU only).

        - ``'lil'``: List of Lists (CPU only).

    """
    from .convert.scipy import to_scipy

    if device == "cpu":
        dtype = dtype if dtype is not None else np.float32
        dtype_int = np.int32
        to_array = np.asarray
        to_matrix = sp.csr_matrix
    elif device == "gpu":
        try:
            import cupy as cp
            import cupyx.scipy.sparse as cpsp
        except ImportError:
            raise ImportError(
                "GPU computation requires cupy and cupyx. "
                "Please install it via `conda install -c conda-forge cupy`."
            )
        dtype = dtype if dtype is not None else cp.float32
        dtype_int = cp.int32
        to_array = cp.asarray
        to_matrix = cpsp.csr_matrix
    else:
        raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")

    TG = [graph] if is_static_graph(graph) else graph

    # Build per-snapshot node lists and global supra-node offsets.
    # Supra-node ID for node u in snapshot t = offsets[t] + local_idx[t][u].
    snapshot_nodes = [list(G.nodes()) for G in TG]
    offsets = [0] * len(TG)
    for t in range(1, len(TG)):
        offsets[t] = offsets[t - 1] + len(snapshot_nodes[t - 1])

    n_nodes = offsets[-1] + len(snapshot_nodes[-1])
    if n_nodes == 0:
        raise ValueError("Graph has no nodes; cannot build supra-adjacency matrix.")

    local_idx = [
        {node: i for i, node in enumerate(nodes)}
        for nodes in snapshot_nodes
    ]

    # Build sparse supra-adjacency on CPU.
    all_rows, all_cols, all_vals = [], [], []
    for t, G in enumerate(TG):
        off = offsets[t]
        A_cpu = to_scipy(G, weight=weight, format="csr", dtype=dtype)
        A_coo = A_cpu.tocoo()
        if A_coo.nnz:
            # Number of non-zero entries is larger than zero.
            all_rows.append((A_coo.row + off).astype(dtype_int, copy=False))
            all_cols.append((A_coo.col + off).astype(dtype_int, copy=False))
            all_vals.append(A_coo.data.astype(dtype, copy=False))

    # Weighted inter-slice couplings.
    interslice_weight = float(interslice_weight or 0)
    interslice_weights = interslice_weights or {}
    if interslice_weight > 0.0:
        wjj = 0 if interslice_directed else 1
        for t in range(len(TG) - 1):
            idx_prev, idx_curr = local_idx[t], local_idx[t + 1]
            off_prev, off_curr = offsets[t], offsets[t + 1]
            rows_c, cols_c, vals_c = [], [], []
            for node in snapshot_nodes[t]:
                # Connect node to itself in the next snapshot, if it exists.
                ii = idx_prev[node] + off_prev
                if node in idx_curr:
                    jj = idx_curr[node] + off_curr
                    wij = interslice_weights.get((t, t + 1), interslice_weight)
                    rows_c.extend((ii, jj))
                    cols_c.extend((jj, ii))
                    vals_c.extend((wij, wij * wjj))
                    if interslice_couple in ("first", "shared"):
                        continue
                # Connect node to first or all its occurrences in subsequent snapshots.
                if interslice_couple in ("first", "all"):
                    for t_ in range(t + 2, len(TG)):
                        off_next, idx_next = offsets[t_], local_idx[t_]
                        if node in idx_next:
                            jj = idx_next[node] + off_next
                            wij = interslice_weights.get((t, t_), interslice_weight)
                            rows_c.extend((ii, jj))
                            cols_c.extend((jj, ii))
                            vals_c.extend((wij, wij * wjj))
                            if interslice_couple == "first":
                                break
            if rows_c:
                all_rows.append(np.asarray(rows_c, dtype=dtype_int))
                all_cols.append(np.asarray(cols_c, dtype=dtype_int))
                all_vals.append(np.asarray(vals_c, dtype=dtype))

    if all_rows:
        # Concatenate COO arrays and build sparse supra-adjacency matrix.
        rows = to_array(np.concatenate(all_rows), dtype=dtype_int)
        cols = to_array(np.concatenate(all_cols), dtype=dtype_int)
        vals = to_array(np.concatenate(all_vals), dtype=dtype)

        A_supra = to_matrix(
            (vals, (rows, cols)),
            shape=(n_nodes, n_nodes),
            dtype=dtype,
        )
    else:
        # No edges in the temporal graph, return empty sparse matrix.
        A_supra = to_matrix((n_nodes, n_nodes), dtype=dtype)

    if format != "csr":
        A_supra = A_supra.asformat(format)

    return (A_supra, offsets) if return_offsets else A_supra


def temporal_edge_similarity(
    TG: TemporalGraph,
    method: Literal["jaccard", "intersect", "overlap", "dice", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns temporal edge presence matrix. Available choices for ``method``:

        - ``'jaccard'``: intersection over union size,
          :math:`\\frac{|A \\cap B|}{|A \\cup B|}`;

        - ``'intersect'``: intersection over size of first set,
          :math:`\\frac{|A \\cap B|}{|A|}`;

        - ``'overlap'``: intersection over size of smaller set,
          :math:`\\frac{|A \\cap B|}{\\min(|A|, |B|)}`;

        - ``'dice'``: double intersection over sum of sizes,
          :math:`\\frac{2|A \\cap B|}{|A| + |B|}`;

        - ``'geometric'``: geometric mean of set overlaps,
          :math:`\\frac{|A \\cap B|^2}{|A| |B|}`.

    .. seealso::

        The `Examples → Algorithms and metrics → Temporal evolution
        <../examples/metrics.html#temporal-evolution>`__  for an example.

    .. rubric:: Example

    Loading and computing similarity among edge sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> tx.temporal_edge_similarity(TG, method="jaccard")

        [[1.0,  0.05, 0.10],
         [0.11, 1.0,  0.08],
         [0.11, 0.08, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param str method: Measure to consider. Default is ``'jaccard'``. Available choices:
        ``'jaccard'``, ``'intersect'``, ``'overlap'``, ``'dice'``, ``'geometric'``.
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    data = {edge: i for i, edge in enumerate(TG.edges(copies=False))}
    data = [[data[edge] for edge in edges] for edges in TG.edges()]
    return _temporal_matrix(data, method=method, na_diag=na_diag)


def temporal_node_similarity(
    TG: TemporalGraph,
    method: Literal["jaccard", "intersect", "overlap", "dice", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns temporal node presence matrix. Available choices for ``method``:

        - ``'jaccard'``: intersection over union size,
          :math:`\\frac{|A \\cap B|}{|A \\cup B|}`;

        - ``'intersect'``: intersection over size of first set,
          :math:`\\frac{|A \\cap B|}{|A|}`;

        - ``'overlap'``: intersection over size of smaller set,
          :math:`\\frac{|A \\cap B|}{\\min(|A|, |B|)}`;

        - ``'dice'``: double intersection over sum of sizes,
          :math:`\\frac{2|A \\cap B|}{|A| + |B|}`;

        - ``'geometric'``: geometric mean of set overlaps,
          :math:`\\frac{|A \\cap B|^2}{|A| |B|}`.

    .. seealso::

        The `Examples → Algorithms and metrics → Temporal evolution
        <../examples/metrics.html#temporal-evolution>`__  for an example.

    .. rubric:: Example

    Loading and computing similarity among node sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> tx.temporal_node_similarity(TG, method="jaccard")

        [[1.0,  1.0,  0.99],
         [1.0,  1.0,  0.99],
         [0.99, 0.99, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param str method: Measure to consider. Default is ``'jaccard'``. Available choices:
        ``'jaccard'``, ``'intersect'``, ``'overlap'``, ``'dice'``, ``'geometric'``.
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    return _temporal_matrix(TG.nodes(), method=method, na_diag=na_diag)


def temporal_split(
    graph: Union[StaticGraph, TemporalGraph, List[int]],
    train_split: float,
    val_split: Optional[float] = None,
    attr: Optional[str] = None,
) -> tuple:
    """
    Create a temporal split for training, validation, and test sets.
    Sets are disjoint time intervals (i.e., unique time steps for each split) and the remaining
    edges after allocating training and validation splits are assigned to the test split.

    Accepts a list of timestamps corresponding to each edge in the temporal graph
    or a temporal graph object and an optional edge `attr` to consider as timestamps.

    Returns ``(train_mask, val_mask, test_mask)`` where each mask is a boolean
    array indicating which edges belong to the respective split.

    :param timestamps: A list of timestamps for each edge.
    :param train_split: Proportion of training edges.
    :param val_split: Proportion of validation edges.
    """
    if is_static_graph(graph):
        if attr is not None:
            raise ValueError("Argument `attr` must be `None` when input is a static graph.")
        timestamps = [
            d.get(attr, None) for _, _, d in graph.edges(data=True)]

    if is_temporal_graph(graph):
        timestamps = [
            d.get(attr, t) for t, G in enumerate(graph) for _, _, d in G.edges(data=True)]

    time = np.array(timestamps)

    for train_time in np.unique(time, return_index=True)[1][::-1]:
        train_mask = time <= train_time
        if train_mask.sum()/len(time) <= train_split:
            break

    for val_time in range(train_time, time.max()+1)[::-1]:
        val_mask = (time > train_time) & (time <= val_time)
        if val_mask.sum()/len(time) <= (val_split or 0):
            break

    test_mask = ~(train_mask|val_mask)
    return train_mask, val_mask, test_mask


def _temporal_matrix(data: list, method: str, na_diag: bool = False) -> List[list]:
    values = []
    for i in range(len(data)):
        values.append([])
        for j in range(len(data)):
            if na_diag and i == j:
                values[i].append(None)
                continue
            data_i = set(data[i])
            data_j = set(data[j])
            intersection = data_i.intersection(data_j)
            union = data_i.union(data_j)
            if method == "jaccard":
                val = (len(intersection) / len(union)
                      ) if len(union) > 0 else 0
            elif method == "intersect":
                val = (len(intersection) / len(data_i)
                      ) if len(data_i) > 0 else 0
            elif method == "overlap":
                val = (len(intersection) / min(len(data_i), len(data_j))
                      ) if min(len(data_i), len(data_j)) > 0 else 0
            elif method == "dice":
                val = (2 * len(intersection) / (len(data_i) + len(data_j))
                      ) if (len(data_i) + len(data_j)) > 0 else 0
            elif method == "geometric":
                val = (len(intersection) ** 2 / (len(data_i) * len(data_j))
                      ) if len(data_i) > 0 and len(data_j) > 0 else 0
            values[i].append(val)
    return values
