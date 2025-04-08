from typing import Union

from ..utils import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_igraph(G: Union[TemporalGraph, StaticGraph, list], *args, **kwargs):
    """
    Convert from NetworkX to `igraph <https://igraph.org/python>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: igraph.Graph

    :note: Wrapper function for
        `igraph.Graph.from_networkx
        <https://igraph.org/python/doc/api/igraph.Graph.html#from_networkx>`__.
    """
    import igraph as ig

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Input must be a temporal or static NetworkX graph."

    if is_temporal_graph(G) or type(G) == list:
        return [to_igraph(H, *args, **kwargs) for H in G]

    return ig.Graph.from_networkx(G, *args, **kwargs)