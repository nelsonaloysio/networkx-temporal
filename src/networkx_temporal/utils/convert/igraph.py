from typing import Union

from ...classes.types import is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_igraph(graph: Union[StaticGraph, TemporalGraph], *args, **kwargs):
    """ Convert from NetworkX to `igraph <https://igraph.org/python>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: igraph.Graph

    :note: Wrapper function for
        `igraph.Graph.from_networkx
        <https://python.igraph.org/en/stable/api/igraph.Graph.html#from_networkx>`__.
    """
    import igraph as ig

    if is_temporal_graph(graph):
        return [to_igraph(g, *args, **kwargs) for g in graph]

    return ig.Graph.from_networkx(graph, *args, **kwargs)