import networkx as nx


def from_events(events: list, directed: bool = False, multigraph: bool = True) -> list:
    """
    Returns temporal graph from sequence of events.

    :param events: List of events, where each event is a tuple (u, v, t) or (u, v, t, e),
        where `u` is the source node, `v` is the target node, `t` is the time of interaction,
        and `e` is either 1 (representing edge addition) or -1 (representing edge deletion).
    :param directed: If True, the graph will be a digraph.
    :param multigraph: If True, the graph will be a multigraph.
    """
    assert events,\
        "Argument `events` must be a non-empty list."

    assert len(events[0]) in (3, 4),\
        f"Each event must have 3 or 4 elements, received: {len(events[0])}."

    t = 1 + max(events, key=lambda x: x[2])[2]

    from ..temporal import TemporalGraph
    TG = TemporalGraph(directed=directed, multigraph=multigraph, t=t)

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


def to_events(self, stream: bool = True) -> list:
    """
    Returns a sequence of events, e.g., (u, v, t), where u and v are nodes
    and t specifies the time of the event, or (u, v, t, e), where e is either
    an edge addition if a positive unit (1) or deletion if a negative unit (-1).

    **Note**: as sequences of events are edge-based, node isolates are not preserved.

    :param stream: If `False`, returns events as 4-tuples, i.e., (u, v, t, e).
    """
    if stream:
        return [(e[0], e[1], t) for t, G in enumerate(self) for e in G.edges()]

    events = []
    for t in range(len(self)):
        if t == 0:
            for edge in self[0].edges():
                events.append((*edge, t, 1))
        else:
            for edge in self[t].edges():
                if not self[t-1].has_edge(*edge):
                    events.append((*edge, t, 1))
            for edge in self[t-1].edges():
                if not self[t].has_edge(*edge):
                    events.append((*edge, t, -1))

    return events