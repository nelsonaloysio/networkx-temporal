from ..typing import TemporalGraph


def from_events(events: list, directed: bool = False, multigraph: bool = True) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.TemporalGraph` object from sequence of events.

    :param list events: List of events, where each event is a tuple :math:`(u, v, t)` or
        :math:`(u, v, t, \\varepsilon)`, where :math:`u` is the source node, :math:`v` is the target
        node, :math:`t` is the time of interaction, and :math:`\\varepsilon` is either ``1``
        (edge addition) or ``-1`` (edge deletion).
    :param bool directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`_.
        Default is ``False``.
    :param bool multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.
        Default is ``True``.

    :rtype: TemporalGraph
    """
    assert events,\
        "Argument `events` must be a non-empty list."

    assert len(events[0]) in (3, 4),\
        f"Each event must have 3 or 4 elements, received: {len(events[0])}."

    t = 1 + max(events, key=lambda x: x[2])[2]

    from ..graph import temporal_graph
    TG = temporal_graph(directed=directed, multigraph=multigraph, t=t)

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
    Returns a sequence of 3-tuples or 4-tuples representing events.

    - **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time
      attribute;

    - **4-tuples** (:math:`u, v, t, \\varepsilon`), where an additional element :math:`\\varepsilon` is
      either a positive (``1``) or negative (``-1``) unity representing edge addition and deletion
      events, respectively.

    .. important::

        Event-based temporal graphs do not currently store node- or edge-level attribute data.
        Moreover, as sequences of events are edge-based, node isolates are not preserved.

    :param bool stream: If ``False``, returns events as 4-tuples. Default is ``True``.
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