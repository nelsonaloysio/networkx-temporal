# cugraph.py

from typing import List, Optional, Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_cugraph(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    weight: Optional[str] = "weight",
    nodelist: Optional[list] = None,
    use_compat_graph: bool = True,
) -> Union[object, List[object]]:
    """ Convert from NetworkX to `cuGraph <https://docs.rapids.ai/api/cugraph/stable/>`__.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``. Ignored if ``use_compat_graph=False``.
    :param nodelist: List of nodes to consider for conversion. If unset, all nodes are considered.
    :param use_compat_graph: If ``True`` (default), returns a NetworkX-compatible graph wrapper.
        If ``False``, returns a native CudaGraph object.

    :note: For versioned documentation, see: `NVIDIA <https://docs.nvidia.com/> Documentation Hub`__.
    """
    try:
        import nx_cugraph as nxcg
    except ImportError as exc:
        raise ImportError(
            "nx-cugraph is required to convert NetworkX graphs to cuGraph. "
            "Please install it via " \
            "`conda install -c rapidsai -c nvidia -c conda-forge "
            "cugraph pylibcugraph nx-cugraph`."
        ) from exc

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    def _to_cugraph(g):
        return nxcg.from_networkx(
            g,
            edge_attrs=weight,
            use_compat_graph=use_compat_graph,
        )

    if nodelist:
        graph = graph.subgraph(nodelist)

    if is_static_graph(graph):
        return _to_cugraph(graph)

    return [_to_cugraph(g) for g in graph]


# scipy.py

from typing import List, Optional, Union

import networkx as nx
import scipy.sparse as sp

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import Literal, StaticGraph, TemporalGraph

try:
    from networkx import from_scipy_sparse_array, to_scipy_sparse_array
except ImportError:  # networkx <= 2.7 (#5262)
    from networkx import (from_scipy_sparse_matrix as from_scipy_sparse_array,
                          to_scipy_sparse_matrix as to_scipy_sparse_array)

FORMAT = Literal["csr", "csc", "dok", "lil"]
FORMATS = list(FORMAT.__args__)


def to_scipy(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    supra: Optional[bool] = False,
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    nodelist: Optional[list] = None,
    dtype: Optional[object] = None,
    format: FORMAT = "csr",
) -> Union[sp.spmatrix, List[sp.spmatrix]]:
    """ Convert from NetworkX to sparse `SciPy <https://scipy.org>`__ matrix.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param supra: If ``True`` and a temporal graph is provided, returns the supra-adjacency
        matrix of the temporal graph instead of a list of adjacency matrices, one per snapshot.
        Default: ``False``.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
    :param nodelist: List of nodes to consider for conversion. If unset, all nodes are considered.
    :param dtype: Data type of the resulting adjacency matrix. If ``None``, the type is inferred.
    :param format: Sparse matrix format. Available choices:
        - ``'csr'``: Compressed Sparse Row (default).
        - ``'csc'``: Compressed Sparse Column.
        - ``'dok'``: Dictionary of Keys (CPU only).
        - ``'lil'``: List of Lists (CPU only).
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    kwargs = {"weight": weight, "dtype": dtype, "format": format}

    if nodelist:
        graph = graph.subgraph(nodelist)

    if is_static_graph(graph):
        return to_scipy_sparse_array(graph, **kwargs)

    if supra:
        from ..graph import to_supra_adjacency_matrix
        return to_supra_adjacency_matrix(
            graph, interslice_weight=interslice_weight, device="cpu", **kwargs
        )

    return [to_scipy_sparse_array(g, **kwargs) for g in graph]


def from_scipy(
    adj: Union[sp.spmatrix, List[sp.spmatrix]],
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    edge_attr: Optional[str] = "weight",
) -> Union[StaticGraph, TemporalGraph]:
    """ Convert from sparse `SciPy <https://scipy.org>`__ matrix to NetworkX.

    :param adj: A SciPy sparse matrix or list of matrices representing graph adjacencies.
    :param directed: If ``True``, returns a directed graph. Default is ``False``.
    :param multigraph: If ``True``, returns a multigraph. Default is ``True``.
    :param edge_attr: Edge attribute key used to store edge weights. Default is ``'weight'``.
    """
    multigraph = True if multigraph is None else multigraph
    create_using = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")

    if isinstance(adj, sp.spmatrix):
        return from_scipy_sparse_array(
            adj,
            parallel_edges=multigraph,
            create_using=create_using,
            edge_attribute=edge_attr,
        )

    from ...transform import from_snapshots
    return from_snapshots([
        from_scipy_sparse_array(
            array,
            parallel_edges=multigraph,
            create_using=create_using,
            edge_attribute=edge_attr,
        )
        for array in adj
    ])
