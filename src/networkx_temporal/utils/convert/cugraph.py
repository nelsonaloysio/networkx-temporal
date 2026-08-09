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

    :note: For versioned documentation, see: `NVIDIA Documentation Hub <https://docs.nvidia.com/>`__.
    """
    try:
        import nx_cugraph as nxcg
    except ImportError as exc:
        raise ImportError(
            "nx-cugraph is required to convert NetworkX graphs to cuGraph. "
            "Please install it via " \
            "`conda install -c rapidsai -c nvidia -c conda-forge "
            "cugraph nx-cugraph pylibcugraph`."
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
