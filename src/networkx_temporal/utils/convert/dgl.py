from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_dgl(G: Union[StaticGraph, TemporalGraph, list], *args, **kwargs):
    """ Convert from NetworkX to `Deep Graph Library <https://www.dgl.ai/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: dgl.DGLGraph

    :note: Wrapper function for
        `dgl.from_networkx
        <https://docs.dgl.ai/en/latest/generated/dgl.from_networkx.html>`__.
    """
    import dgl

    if not (is_temporal_graph(G) or is_static_graph(G) or type(G) != list):
        raise TypeError("Input must be one or a sequence of temporal or static NetworkX graphs.")

    if is_temporal_graph(G) or type(G) == list:
        return [dgl.from_networkx(H, *args, **kwargs) for H in G]

    return dgl.from_networkx(G, *args, **kwargs)
