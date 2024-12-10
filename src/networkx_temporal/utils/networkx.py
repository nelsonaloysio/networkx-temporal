from typing import Any, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def from_multigraph(G: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """
    Returns a graph from a multigraph object.

    Parallel (multiple) edges among nodes are converted to single edges, with a ``weight`` attribute
    storing their total occurrences. If the attribute already exists, their total sum is stored instead.

    .. attention::

        Converting a multigraph to a graph object may result in data loss: multiple parwise edges
        are merged into single ones, with later edge attributes taking precedence over earlier ones.

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

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    """
    from ..graph import temporal_graph

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Argument `graph` must be either a temporal or static NetworkX graph object."

    if not is_temporal_graph(G):
        return _from_multigraph(G)

    TG = temporal_graph(directed=G.is_directed(), multigraph=False)
    TG.data = [_from_multigraph(H) for H in G]
    TG.name = G.name
    TG.names = G.names
    return TG


def is_frozen(G: Union[TemporalGraph, StaticGraph], on_each: bool = False) -> bool:
    """
    Returns ``True`` if graph is frozen, ``False`` otherwise.

    A frozen graph is immutable, meaning that nodes and edges cannot be added or removed.
    Calling ``copy`` on a frozen graph returns a (mutable) deep copy of the graph object.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph` or static NetworkX graph object.
    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    assert is_temporal_graph(graph) or is_static_graph(TG),\
        "Argument `graph` must be a temporal graph or a static graph."

    if is_static_graph(graph):
        return nx.is_frozen(graph)

    return [nx.is_frozen(G) for G in graph] if on_each else nx.is_frozen(graph[0])


def is_static_graph(G: Any) -> bool:
    """
    Returns ``True`` if object is a static graph, ``False`` otherwise.

    Matches any of: NetworkX
    `Graph <https://networkx.org/documentation/stable/reference/classes/graph.html>`__,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__,
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__.

    :param G: Object to check.
    """
    return not is_temporal_graph(G) and isinstance(G, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph))


def is_temporal_graph(G: Any) -> bool:
    """
    Returns ``True`` if object is a temporal graph, ``False`` otherwise.

    Matches any of:
    :class:`~networkx_temporal.graph.TemporalGraph`,
    :class:`~networkx_temporal.graph.TemporalDiGraph`,
    :class:`~networkx_temporal.graph.TemporalMultiGraph`,
    :class:`~networkx_temporal.graph.TemporalMultiDiGraph`.

    :param G: Object to check.
    """
    from ..graph import TemporalBase, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    return isinstance(G, (TemporalBase, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph))


def to_multigraph(G: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """
    Returns a multigraph from a graph object.

    A multigraph is a graph that allows multiple (parallel) edges between pairwise nodes.

    .. seealso::

        The :func:`~networkx_temporal.utils.from_multigraph`
        function to convert a multigraph to a graph object.

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    """
    from ..graph import temporal_graph

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Argument `graph` must be either a temporal or NetworkX graph object."

    if not is_temporal_graph(G):
        return _to_multigraph(G)

    TG = temporal_graph(directed=G.is_directed(), multigraph=True)
    TG.data = [_to_multigraph(H) for H in G]
    TG.name = G.name
    TG.names = G.names
    return TG


def _from_multigraph(G: nx.MultiGraph) -> StaticGraph:
    """ Returns a multigraph object from a graph. """
    H = getattr(nx, f"{f'Di' if G.is_directed() else ''}Graph")()
    H.add_edges_from(G.edges(data=True))

    weight = {}
    for u, v, w in G.edges(data="weight", default=1):
        weight[(u, v)] = weight.get((u, v), 0) + w

    nx.set_edge_attributes(H, weight, "weight")
    return H


def _to_multigraph(G: nx.MultiGraph) -> StaticGraph:
    """ Returns a graph object from a multigraph. """
    H = getattr(nx, f"Multi{f'Di' if G.is_directed() else ''}Graph")()
    H.add_edges_from(G.edges(data=True))
    return H
