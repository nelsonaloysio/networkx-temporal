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
    yield from {nbr for G in TG if G.has_node(node) for nbr in nx.all_neighbors(G, node)}

def neighbors(TG: TemporalGraph, node: Any) -> iter:
    """ Returns iterator of node neighbors in each snapshot. Considers edge direction.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param node: Node to get neighbors for.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    yield from {nbr for G in TG if G.has_node(node) for nbr in G.neighbors(node) }


def compose(
    G1: Union[TemporalGraph, StaticGraph],
    G2: Union[TemporalGraph, StaticGraph],
) -> Union[TemporalGraph, StaticGraph]:
    """ Returns the union of two graphs.
    For temporal graphs, the snapshots of each graph are concatenated in order,
    so that the resulting object contains both input snapshots.

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
    so that the resulting object contains all input snapshots.

    :param object graphs: A list of :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph objects.
    """
    if type(graphs) != list:
        raise TypeError(f"Argument `graphs` must be a list, received: {type(graphs)}.")
    if len(graphs) == 0:
        raise ValueError("Argument `graphs` must contain at least one graph.")

    static = all(is_static_graph(g) for g in graphs)
    temporal = all(is_temporal_graph(g) for g in graphs)
    if not (static or temporal):
        raise NetworkXError("All inputs must be either temporal or static NetworkX graphs.")

    all_digraph = all(g.is_directed() for g in graphs)
    any_digraph = any(g.is_directed() for g in graphs)
    if any_digraph and not all_digraph:
        raise NetworkXError("All inputs must be either directed or undirected graphs.")

    all_multigraph = all(g.is_multigraph() for g in graphs)
    any_multigraph = any(g.is_multigraph() for g in graphs)
    if any_multigraph and not all_multigraph:
        raise NetworkXError("All inputs must be either multigraph or non-multigraph objects.")

    if static:
        return nx.compose_all([g for g in graphs])

    TG = graphs[0].__class__(t=0)
    for temporal_graph in graphs:
        TG.add_snapshots_from(temporal_graph.graphs)

    return TG


def create_empty_copy(
    graph: Union[TemporalGraph, StaticGraph],
) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a copy of the input graph structure without edge data.

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if is_static_graph(graph):
        return nx.create_empty_copy(graph)
    TG = graph.__class__(t=0)
    for g in graph:
        TG.append(nx.create_empty_copy(g))
    return TG


def edge_subgraph(self: TemporalGraph, edges: list) -> TemporalGraph:
    """ Returns a subgraph view of the temporal graph containing only the specified edges.

    :param edges: A list of edges to include in the subgraph.
    """
    TG = self.__class__(t=0)
    TG.graphs = {t: G.edge_subgraph(edges) for t, G in self.items()}
    return TG

def subgraph(self: TemporalGraph, nodes: list) -> TemporalGraph:
    """ Returns a subgraph view of the temporal graph containing only the specified nodes.

    :param nodes: A list of nodes to include in the subgraph.
    """
    TG = self.__class__(t=0)
    TG.graphs = {t: G.subgraph(nodes) for t, G in self.items()}
    return TG


def from_multigraph(graph: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a graph from a multigraph object.

    Parallel (multiple) edges among nodes are converted to single edges, with a ``weight``
    attribute storing their total occurrences. If the attribute exists, their total
    sum is stored instead.

    .. attention::

        Converting a multigraph to a graph object may result in data loss: multiple pairwise
        edges are merged, with later attributes other than ``weight`` taking
        precedence over earlier ones.

    .. rubric:: Example

    Converting a static multigraph to a graph, summing the weights of parallel edges:

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

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from . import TemporalGraph, TemporalDiGraph

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if not graph.is_multigraph():
        return graph

    if is_static_graph(graph):
        H = nx.DiGraph() if graph.is_directed() else nx.Graph()
        H.graph = graph.graph.copy()
        H.add_nodes_from(graph.nodes(data=True))
        H.add_edges_from(graph.edges(data=True))
        # Aggregate weights of parallel edges.
        weight = {}
        for u, v, w in graph.edges(data="weight", default=1):
            weight[(u, v)] = weight.get((u, v), 0) + w
        if any(w > 1 for w in weight.values()):
            nx.set_edge_attributes(H, weight, "weight")
        return H

    TG = TemporalDiGraph(t=0) if graph.is_directed() else TemporalGraph(t=0)
    TG.add_snapshots_from([from_multigraph(H) for H in graph])
    TG.name = graph.name
    TG.index = graph.index
    return TG


def to_multigraph(graph: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """ Returns a multigraph from a graph object. SImilar to
    The :func:`~networkx_temporal.utils.from_multigraph`.

    A multigraph is a graph that allows multiple (parallel) edges between pairwise nodes.

    .. attention::

        This function does not duplicate edges with a ``weight`` attribute larger than one, but
        simply converts the graph to a multigraph format, allowing for parallel edges to be added.

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from . import TemporalMultiGraph, TemporalMultiDiGraph

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Argument `graph` must be either a temporal or NetworkX graph object.")

    if graph.is_multigraph():
        return graph

    if is_static_graph(graph):
        H = nx.MultiDiGraph() if graph.is_directed() else nx.MultiGraph()
        H.graph = graph.graph.copy()
        H.add_nodes_from(graph.nodes(data=True))
        H.add_edges_from(graph.edges(data=True))
        return H

    TG = TemporalMultiDiGraph(t=0) if graph.is_directed() else TemporalMultiGraph(t=0)
    TG.add_snapshots_from([to_multigraph(H) for H in graph])
    TG.name = graph.name
    TG.index = graph.index
    return TG


def isolates(self) -> list:
    """ Returns list of node isolates in each snapshot.
    """
    return [list(nx.isolates(G)) for G in self]


def relabel_nodes(
    graph: Union[TemporalGraph, StaticGraph],
    mapping: Union[dict, list],
    copy: bool = True,
) -> Union[TemporalGraph, StaticGraph]:
    """ Relabels nodes of a graph according to a given mapping.

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param mapping: A dictionary or list defining the node relabeling.
    :param copy: Whether to return a new graph object (default) or modify
        the input graph in place.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if is_static_graph(graph):
        return nx.relabel_nodes(graph, mapping, copy=copy)
    TG = graph.__class__(t=0)
    TG.graphs = {t: nx.relabel_nodes(g, mapping, copy=copy) for t, g in graph.items()}
    return TG


def set_edge_attributes(
    graph: Union[TemporalGraph, StaticGraph],
    values: Any,
    name: str,
) -> Union[TemporalGraph, StaticGraph]:
    """ Sets edge attributes for a graph.

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param values: Edge attribute data. Can be a single scalar or dictionary
        (applied to all snapshots), or a list of such values (one per snapshot).
    :param name: The edge attribute key.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if is_static_graph(graph):
        nx.set_edge_attributes(graph, name=name, values=values)
        return graph
    for t, g in enumerate(graph):
        nx.set_edge_attributes(g, name=name, values=values[t] if type(values) == list else values)
    return graph

def set_node_attributes(
    graph: Union[TemporalGraph, StaticGraph],
    values: Any,
    name: str,
) -> Union[TemporalGraph, StaticGraph]:
    """ Sets node attributes for a graph.

    :param object graph: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param values: Node attribute data. Can be a single scalar or dictionary
        (applied to all snapshots), or a list of such values (one per snapshot).
    :param name: The node attribute key.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_static_graph(graph):
        nx.set_node_attributes(graph, name=name, values=values)
        return graph

    for t, g in enumerate(graph):
        nx.set_node_attributes(g, name=name, values=values[t] if type(values) == list else values)

    return graph
