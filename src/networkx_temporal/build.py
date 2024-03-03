from typing import Optional, Union

import networkx as nx

from .temporal import TemporalGraph


def from_events(
    events: list,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None
) -> list:
    """
    Returns temporal graph from sequence of events, i.e., (u, v, t) or (u, v, t, e).

    :param events: List of events, where each event is a tuple (u, v, t) or (u, v, t, e).
    :param directed: If True, the graph will be directed.
    :param multigraph: If True, the graph will be a multigraph.
    """
    assert events,\
        "Argument `events` must be a non-empty list."

    assert len(events[0]) in (3, 4),\
        f"Each event must have 3 or 4 elements, received: {len(events[0])}."

    TG = TemporalGraph(directed=directed,
                       multigraph=multigraph,
                       t=1 + max(events, key=lambda x: x[2])[2])

    if len(events[0]) == 3:
        list(TG[t].add_edge(u, v) for u, v, t in events)

    if len(events[0]) == 4:
        temporal_edges = {}
        for u, v, t, e in events:
            if e == 1:
                temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [t]
            if e == -1:
                for t_ in range(1 + temporal_edges[(u, v)][-1], t):
                    temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [t_]

        list(TG[t].add_edge(u, v) for (u, v), ts in temporal_edges.items() for t in ts)

    return TG


def from_snapshots(graphs: Union[dict, list]) -> list:
    """
    Returns temporal graph from sequence of snapshots.

    :param graphs: List or dictionary of NetworkX graphs
    """
    T = list(graphs.keys()) if type(graphs) == dict else range(len(graphs))

    directed = graphs[T[0]].is_directed()
    multigraph = graphs[T[0]].is_multigraph()

    assert type(graphs) in (dict, list),\
           "Argument `graphs` must be a list or dictionary of NetworkX graphs."

    assert len(graphs) > 0,\
           "Argument `graphs` must be a non-empty list or dictionary."

    assert all(type(graphs[t]) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for t in T),\
            "All elements in data must be valid NetworkX graphs."

    assert all(directed == graphs[T[t]].is_directed() for t in T),\
           "Mixed graphs and digraphs are not supported."

    assert all(multigraph == graphs[T[t]].is_multigraph() for t in T),\
           "Mixed graphs and multigraphs are not supported."

    TG = TemporalGraph(directed=directed, multigraph=multigraph)
    TG.data = graphs
    return TG


def from_static(G: nx.Graph) -> dict:
    """
    Returns temporal graph from a static graph.

    :param G: NetworkX graph.
    """
    return from_snapshots([G])


def from_unified(UTG: nx.Graph) -> list:
    """
    Returns temporal graph from unified temporal graph (UTG).

    Note that the UTG must be a valid unified temporal graph, i.e., it must contain
    temporal nodes in the format `node_timestamp`, where `node` is the original node
    name and `timestamp` is a non-negative integer.

    :param UTG: Unified temporal graph.
    """
    temporal_nodes = {}

    for node in UTG.nodes():
        t = node.rsplit("_", 1)[-1]

        assert t.isdigit(),\
               f"Unified temporal graph (UTG) contains non-temporal nodes ('{node}')."

        temporal_nodes[t] = temporal_nodes.get(t, []) + [node]

    return from_snapshots([
        nx.relabel_nodes(
            UTG.subgraph(temporal_nodes[t]),
            {v: v.rsplit("_", 1)[0] for v in temporal_nodes[t]}
        )
        for t in sorted(temporal_nodes.keys(), key=int)
    ])
