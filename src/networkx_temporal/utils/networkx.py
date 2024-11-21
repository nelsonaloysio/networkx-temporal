from typing import Union

import networkx as nx

from ..typing import TemporalGraph, StaticGraph


def from_multigraph(graph: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, nx.Graph, nx.DiGraph]:
    """
    Returns a graph object without parallel edges from a static or temporal multigraph.

    Multiple edges among pairwise nodes are converted to single edges, with a ``weight`` attribute
    storing their total occurrences. If the attribute already exists, their total sum is stored instead.

    .. attention::

        Converting a multigraph to a graph object may result in data loss: multiple parwise edges
        are merged into single ones, with only the attributes in the latest occurrence being preserved.

    .. rubric:: Example

    .. code-block:: python

       >>> import networkx as nx
       >>> from networkx_temporal import from_multigraph
       >>>
       >>> G = nx.MultiGraph()
       >>> G.add_edge(1, 2, weight=2)
       >>> G.add_edge(1, 2, weight=3)
       >>>
       >>> H = from_multigraph(G)
       >>> print(H.edges(data=True))

       [(1, 2, {'weight': 5})]

    :param object graph: :class:`~networkx_temporal.graph.TemporalGraph` or static NetworkX graph object.
    """
    from ..graph import is_temporal_graph, temporal_graph

    assert is_temporal_graph(graph) or isinstance(graph, StaticGraph.__args__),\
        "Argument `graph` must be either a temporal or static NetworkX graph object."

    if not is_temporal_graph(graph):
        return _from_multigraph(graph)

    TG = temporal_graph(directed=graph.is_directed(), multigraph=False)
    TG.data = [_from_multigraph(G) for G in graph]
    TG.name = graph.name
    return TG


def to_multigraph(graph: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, nx.MultiGraph, nx.MultiDiGraph]:
    """
    Returns a multigraph object from a static or temporal graph.

    A multigraph is a graph that allows multiple (parallel) edges between pairwise nodes.

    .. seealso::

        The :func:`~networkx_temporal.utils.from_multigraph` function to convert a multigraph to a graph object.

    :param object graph: :class:`~networkx_temporal.graph.TemporalGraph` or static NetworkX graph object.
    """
    from ..graph import is_temporal_graph, temporal_graph

    assert is_temporal_graph(graph) or isinstance(graph, StaticGraph.__args__),\
        "Argument `graph` must be either a temporal or NetworkX graph object."

    if not is_temporal_graph(graph):
        return _to_multigraph(graph)

    TG = temporal_graph(directed=graph.is_directed(), multigraph=True)
    TG.data = [_to_multigraph(G) for G in graph]
    TG.name = graph.name
    return TG


def _from_multigraph(G: nx.MultiGraph) -> nx.Graph:
    """ Returns a multigraph object from a graph. """
    H = getattr(nx, f"{f'Di' if G.is_directed() else ''}Graph")()
    H.add_edges_from(G.edges(data=True))

    weight = {}
    for u, v, w in G.edges(data="weight", default=1):
        weight[(u, v)] = weight.get((u, v), 0) + w

    nx.set_edge_attributes(H, weight, "weight")
    return H


def _to_multigraph(G: nx.MultiGraph) -> nx.Graph:
    """ Returns a graph object from a multigraph. """
    H = getattr(nx, f"Multi{f'Di' if G.is_directed() else ''}Graph")()
    H.add_edges_from(G.edges(data=True))
    return H
