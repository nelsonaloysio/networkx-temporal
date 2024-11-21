from collections import Counter
from typing import Optional, Union

import networkx as nx

from ..typing import Literal, TemporalGraph, StaticGraph

EPSILON = {"int": int, "float": float}


def from_events(events: list, directed: bool = None, multigraph: bool = None, as_view: bool = True) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.graph.TemporalGraph` from a list of 3-tuples or
    4-tuples representing edge-level events.

    - **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time
      attribute;

    - **4-tuples** (:math:`u, v, t, \\varepsilon`), where :math:`\\varepsilon` is either an
      integer for edge addition (``1``) or deletion (``-1``) event, or a float defining the
      duration of the pairwise interaction (zero for a single snapshot).

    .. seealso::

        The `Convert and transform → Graph representations
        <../examples/convert.html#graph-representations>`__
        page for details and examples.

    :param list events: List of 3-tuple or 4-tuple edge-level events.
    :param bool directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`_.
        Default is ``False``.
    :param bool multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.
        Automatically set to ``False`` if parallel edges are not found, ``True`` otherwise.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.

    :rtype: TemporalGraph
    """
    from ..graph import temporal_graph

    assert events,\
        "Argument `events` must be a non-empty list."
    assert len(events[0]) in (3, 4),\
        f"Each event must have 3 or 4 elements, received: {len(events[0])}."
    assert len(events[0]) == 3 or type(events[0][-1]) in (int, float),\
        "The last element of each event must be either an integer (1, -1) or a float."

    if len(events[0]) == 3:

        if multigraph is None:
            multigraph = 1 != max(Counter((e[:2] for e in events)).values())

        TG = temporal_graph(directed=directed, multigraph=multigraph)
        list(TG.add_edge(u, v, time=t) for u, v, t in events)

    elif len(events[0]) == 4 and type(events[0][-1]) == int:
        t_max = 1 + max(events, key=lambda x: x[2])[2]
        temporal_edges = {}

        for u, v, t, e in events:
            if e == 1:
                temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [range(t, t_max)]
            elif e == -1:
                temporal_edges[(u, v)][-1] = range(temporal_edges[(u, v)][-1].start, t)
            else:
                raise ValueError(f"Expected edge events to be either 1 or -1, received: {e}.")

        if multigraph is None:
            multigraph = any(len(ranges) > 1 or len(ranges[0]) > 1 for ranges in temporal_edges.values())

        TG = temporal_graph(directed=directed, multigraph=multigraph)
        list(TG.add_edge(u, v, time=t) for (u, v), ranges in temporal_edges.items() for r in ranges for t in r)

    elif len(events[0]) == 4 and type(events[0][-1]) == float:

        if multigraph is None:
            multigraph = any(e[-1] > 0 for e in events) or 1 != max(Counter((e[:2] for e in events)).values())

        TG = temporal_graph(directed=directed, multigraph=multigraph)

        for u, v, t, e in events:
            for i in range(t, t + 1 + int(e)):
                TG.add_edge(u, v, time=i)

    TG = TG.slice(attr="time")
    return TG if as_view else TG.copy()


def to_events(TG: TemporalGraph, eps: Optional[Literal["int", "float"]] = None, attr: Optional[str] = None) -> list:
    """
    Returns a list of 3-tuples or 4-tuples representing edge-level events.

    - **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time
      attribute;

    - **4-tuples** (:math:`u, v, t, \\varepsilon`), where :math:`\\varepsilon` is either an
      integer for edge addition (``1``) or deletion (``-1``) event, or a float defining the
      duration of the pairwise interaction (zero for a single snapshot).

    .. important::

        As sequences of events are edge-based, node isolates without self-loops are not preserved.
        Node and edge attributes are also not returned with the event tuples.

    :param TemporalGraph TG: Temporal graph object.
    :param eps: Defines which additional parameter :math:`\\varepsilon` should be returned.

        * If ``None``, returns events as 3-tuples. Default.

        * If ``'int'``, returns events as 4-tuples with an additional parameter representing
          edge addition (``1``) or deletion (``-1``) events.

        * If ``'float'``, returns events as 4-tuples with an additional parameter representing
          the duration of the pairwise interaction.

    :param str attr: Edge attribute to consider when ``eps`` is ``'float'``. If provided, the
        duration of the pairwise interaction is calculated based on the attribute value
        instead of the number of time steps. Optional.

    :note: Available both as a function and as a method from :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    eps = EPSILON.get(eps, eps)

    if type(TG) in StaticGraph.__args__:
        TG = [TG]  # Allows a single graph to be passed as input.

    assert eps in (None, int, float),\
        f"Argument `eps` must be either `int` or `float` if provided."
    assert attr is None or type(attr) == str,\
        f"Argument `attr` must be a string if provided."
    assert attr is None or not any(TG.is_multigraph(on_each=True)),\
        "Edge attributes are not supported when converting multigraphs to events; " \
        "consider calling the `slice` method or converting it with `from_multigraph` beforehand."
    # Filtered (frozen) multigraphs produce inconsistent results. [networkx/networkx#7724]
    assert not any(G.is_multigraph() and nx.is_frozen(G) for G in TG),\
        "Frozen multigraphs are not supported; consider calling the `copy` method beforehand."

    # 3-tuples of format: (u, v, t).
    if not eps:
        return [(e[0], e[1], t) for t, G in enumerate(TG) for e in G.edges()]

    # 4-tuples of format: (u, v, t, int_edge_addition_or_deletion).
    if eps == int:
        events = []
        for t in range(len(TG)):
            if t == 0:
                for edge in TG[0].edges():
                    events.append((*edge, t, 1))
            else:
                for edge in TG[t].edges():
                    if not TG[t-1].has_edge(*edge):
                        events.append((*edge, t, 1))
                for edge in TG[t-1].edges():
                    if not TG[t].has_edge(*edge):
                        events.append((*edge, t, -1))

    # 4-tuples of format: (u, v, t, float_edge_duration).
    if eps == float:
        events = []

        for i in range(len(TG)):
            for u, v, start in TG[i].edges(data=attr, default=i):
                if i == 0 or not TG[i-1].has_edge(u, v):
                    for j in range(i+1, len(TG)):
                        if not TG[j].has_edge(u, v):
                            end = TG[j-1].edges[u, v].get(attr, j) if attr else j
                            events.append((u, v, start, float(end - start - 1)))
                            break
                        if j == len(TG) - 1:
                            end = TG[j-1].edges[u, v].get(attr, j) if attr else j
                            events.append((u, v, start, float(end - start)))
                            break
                    if i == len(TG) - 1:
                        events.append((u, v, start, 0.0))

    return events
