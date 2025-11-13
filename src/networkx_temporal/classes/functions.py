from functools import reduce
from operator import or_
from typing import Any, List, Union

import networkx as nx
from networkx import NetworkXError

from .types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph


def all_neighbors(TG: TemporalGraph, node: Any) -> iter:
    """ Returns iterator of all node neighbors in each snapshot. Does not consider edge direction.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param node: Node to get neighbors for.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    yield from reduce(
        or_,  # lambda x, y: x.union(y),
        iter(set(nx.all_neighbors(G, node)) if G.has_node(node) else set() for G in TG)
    )

def neighbors(TG: TemporalGraph, node: Any) -> iter:
    """ Returns iterator of node neighbors in each snapshot. Considers edge direction.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param node: Node to get neighbors for.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    yield from reduce(
        or_,  # lambda x, y: x.union(y),
        iter(set(nx.neighbors(G, node)) if G.has_node(node) else set() for G in TG)
    )


def compose(
    G1: Union[TemporalGraph, StaticGraph],
    G2: Union[TemporalGraph, StaticGraph],
) -> Union[TemporalGraph, StaticGraph]:
    """ Returns the union of two graphs.
    For temporal graphs, the snapshots of each graph are concatenated in order,
    so that the resulting object contains all input graph snapshots.

    :param object G1: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param object G2: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    return compose_all([G1, G2])

def compose_all(
    graphs: Union[List[TemporalGraph], List[StaticGraph]],
) -> Union[TemporalGraph, StaticGraph]:
    """ Returns the union of multiple graphs.
    For temporal graphs, the snapshots of each graph are concatenated in order,
    so that the resulting object contains all input graph snapshots.

    :param object graphs: A list of :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph objects.
    """
    if type(graphs) != list:
        raise TypeError(f"Argument `graphs` must be a list, received: {type(graphs)}.")
    if len(graphs) == 0:
        raise ValueError("Argument `graphs` must contain at least one graph.")

    static = all(is_static_graph(G) for G in graphs)
    temporal = all(is_temporal_graph(G) for G in graphs)
    if not (static or temporal):
        raise NetworkXError("All inputs must be either temporal or static NetworkX graphs.")

    multigraph = all(G.is_multigraph() for G in graphs)
    if not multigraph:
        raise NetworkXError("All inputs must be either multigraph or non-multigraph objects.")

    if static:
        return nx.compose_all([G for G in graphs])
    if not temporal:
        raise NetworkXError("All inputs must be temporal NetworkX graphs.")

    TG = graphs[0].__class__(t=0)
    for temporal_graph in graphs:
        TG.graphs.extend(temporal_graph.graphs)

    return TG


def create_empty_copy(
    G: Union[StaticGraph, TemporalGraph],
) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a copy of the input graph structure without edge data.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_static_graph(G):
        return nx.create_empty_copy(G)

    TG = G.__class__(t=0)
    for g in G:
        TG.append(nx.create_empty_copy(g))
    return TG


def from_multigraph(G: Union[StaticGraph, TemporalGraph]) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a graph from a multigraph object.

    Parallel (multiple) edges among nodes are converted to single edges, with a ``weight``
    attribute storing their total occurrences. If the attribute already exists, their total
    sum is stored instead.

    .. attention::

        Converting a multigraph to a graph object may result in data loss: multiple parwise
        edges are merged, with later edge attributes taking precedence over earlier ones.

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

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from . import TemporalGraph, TemporalDiGraph

    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if not G.is_multigraph():
        return G

    if is_static_graph(G):
        H = nx.DiGraph() if G.is_directed() else nx.Graph()
        H.add_nodes_from(G.nodes(data=True))
        H.add_edges_from(G.edges(data=True))
        # Aggregate weights of parallel edges.
        weight = {}
        for u, v, w in G.edges(data="weight", default=1):
            weight[(u, v)] = weight.get((u, v), 0) + w
        nx.set_edge_attributes(H, weight, "weight")
        return H

    TG = TemporalDiGraph(t=0) if G.is_directed() else TemporalGraph(t=0)
    TG.graphs.extend([from_multigraph(H) for H in G])
    TG.names = G.names
    return TG

def to_multigraph(G: Union[StaticGraph, TemporalGraph]) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a multigraph from a graph object.

    A multigraph is a graph that allows multiple (parallel) edges between pairwise nodes.

    .. seealso::

        The :func:`~networkx_temporal.utils.from_multigraph`
        function to convert a multigraph to a graph object.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from . import TemporalMultiGraph, TemporalMultiDiGraph

    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Argument `graph` must be either a temporal or NetworkX graph object.")

    if G.is_multigraph():
        return G

    if is_static_graph(G):
        H = nx.MultiDiGraph() if G.is_directed() else nx.MultiGraph()
        H.add_nodes_from(G.nodes(data=True))
        H.add_edges_from(G.edges(data=True))
        return H

    TG = TemporalMultiDiGraph(t=0) if G.is_directed() else TemporalMultiGraph(t=0)
    TG.graphs.extend([to_multigraph(H) for H in G])
    TG.names = G.names
    return TG


def set_edge_attributes(
    G: Union[StaticGraph, TemporalGraph],
    attr: str,
    values: Any,
) -> Union[TemporalGraph, StaticGraph]:
    """ Sets node attributes for a graph.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key.
    :param values: Node attribute data. Can be a single value
        (applied to all snapshots) or a list of such values (one per snapshot).
    """
    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_static_graph(G):
        nx.set_node_attributes(G, attr=attr, values=values)
        return G

    for t, g in enumerate(G):
        nx.set_node_attributes(g, attr=attr, values=values[t] if type(values) == list else values)

    return G

def set_node_attributes(
    G: Union[StaticGraph, TemporalGraph],
    attr: str,
    values: Any,
) -> Union[TemporalGraph, StaticGraph]:
    """ Sets node attributes for a graph.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key.
    :param values: Node attribute data. Can be a single value
        (applied to all snapshots) or a list of such values (one per snapshot).
    """
    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_static_graph(G):
        nx.set_node_attributes(G, attr=attr, values=values)
        return G

    for t, g in enumerate(G):
        nx.set_node_attributes(g, attr=attr, values=values[t] if type(values) == list else values)

    return G
