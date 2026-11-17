from typing import Union

from ...classes.types import is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_dgl(graph: Union[StaticGraph, TemporalGraph], *args, **kwargs):
    """ Convert from NetworkX to `Deep Graph Library <https://www.dgl.ai/>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: dgl.DGLGraph

    :note: Wrapper function for
        `dgl.from_networkx
        <https://docs.dgl.ai/en/latest/generated/dgl.from_networkx.html>`__.
    """
    import dgl

    if is_temporal_graph(graph):
        return [to_dgl(g, *args, **kwargs) for g in graph]

    return dgl.from_networkx(graph, *args, **kwargs)
