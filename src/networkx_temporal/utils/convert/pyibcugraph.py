from typing import List, Optional, Union

import numpy as np

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_pylibcugraph(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    weight: Optional[str] = "weight",
    nodelist: Optional[list] = None,
) -> Union[object, List[object]]:
    """ Convert from NetworkX to `cuGraph <https://docs.rapids.ai/api/cugraph/stable/>`__.

    .. note::

       Edge weights are only supported if ``use_compat_graph=True`` (default), if ``False``, the
       function returns a native CudaGraph object, where all edge weights are considered as ``1``.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``. Ignored if ``use_compat_graph=False``.
    :param nodelist: List of nodes to consider for conversion. If unset, all nodes are considered.
    :param dtype: Data type of the intermediate adjacency matrix. Defaults to ``float32``.
    :param use_compat_graph: If ``True`` (default), returns a NetworkX-compatible graph wrapper.
        If ``False``, returns a native CudaGraph object.

    :note: For versioned documentation, see: `NVIDIA Documentation Hub <https://docs.nvidia.com/>`__.
    """
    try:
        import cupy as cp
        import pylibcugraph as plc
    except ImportError as exc:
        raise ImportError(
            "nx-cugraph is required to convert NetworkX graphs to cuGraph. "
            "Please install it via " \
            "`conda install -c rapidsai -c nvidia -c conda-forge "
            "cugraph pylibcugraph nx-cugraph`."
        ) from exc

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    def _to_pylibcugraph(edgelist):
        srcs = cp.array([e[0] for e in edgelist for e in e], dtype=np.int32)
        dsts = cp.array([e[1] for e in edgelist for e in e], dtype=np.int32)
        weights = cp.array([e[-1] for e in edgelist for e in e], dtype=np.float32)

        graph_props = plc.GraphProperties(
            is_symmetric=not graph.is_directed(),
            is_multigraph=graph.is_multigraph(),
        )

        return plc.SGGraph(
            plc.ResourceHandle(),
            graph_props,
            srcs,
            dsts,
            weight_array=weights,
            store_transposed=True,
            renumber=False,
            do_expensive_check=False,
        )

    edgelist = graph.edges(nodelist, data=weight)

    if is_static_graph(graph):
        return _to_pylibcugraph([edgelist])

    return _to_pylibcugraph(edgelist)
