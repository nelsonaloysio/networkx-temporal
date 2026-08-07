from typing import List, Optional, Union

import networkx as nx

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import Literal, StaticGraph, TemporalGraph

FORMAT = Literal["csr", "csc"]  # "dok", "lil": NotImplementedError (cupy <= 8.6.0)
FORMATS = list(FORMAT.__args__)


def to_cupy(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    supra: Optional[bool] = False,
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    nodelist: Optional[list] = None,
    dtype: Optional[object] = None,
    format: FORMAT = "csr",
) -> Union[object, List[object]]:
    """ Convert from NetworkX to sparse `CuPy <https://cupy.dev>`__ matrix.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param supra: If ``True`` and a temporal graph is provided, returns the supra-adjacency
        matrix of the temporal graph instead of a list of adjacency matrices, one per snapshot.
        Default: ``False``.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
    :param nodelist: List of nodes to consider for conversion. If unset, all nodes are considered.
    :param dtype: Data type of the intermediate adjacency matrix. Defaults to ``float32``.
    :param format: Sparse matrix format. Available choices:
        - ``'csr'``: Compressed Sparse Row (default).
        - ``'csc'``: Compressed Sparse Column.
    """
    from ..graph import to_supra_adjacency_matrix

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    kwargs = {"weight": weight, "dtype": dtype, "format": format, "device": "gpu"}

    if nodelist:
        graph = graph.subgraph(nodelist)

    if is_static_graph(graph):
        return to_supra_adjacency_matrix(graph, **kwargs)

    if supra:
        return to_supra_adjacency_matrix(graph, interslice_weight=interslice_weight, **kwargs)

    return [to_supra_adjacency_matrix(g, **kwargs) for g in graph]
