from collections import Counter
from typing import Any, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def is_events_graph(events: list) -> bool:
    """ Returns ``True`` if events correspond to a graph. List of events corresponds to a graph if
    it is a list of 3-tuples or 4-tuples with the last element being an integer ``(-1, 1)``
    or a non-negative float.

    .. seealso::

        The :func:`~networkx_temporal.transform.from_events` function for details on
        supported event formats.

    :param list events: List of 3-tuple or 4-tuple edge-level events.
    """
    # (u, v, t)
    if len(events[0]) == 3 and all(type(e[2]) == int for e in events):
        return True
    # (u, v, t, e), where e is an integer in (-1, 1)
    elif len(events[0]) == 4 and all(e[-1] in (-1, 1) for e in events):
        return True
    # (u, v, t, e), where e is a (non-negative) float defining the duration of the interaction
    elif len(events[0]) == 4 and all(type(e[-1]) == float and e[-1] >= 0 for e in events):
        return True
    return False


def is_events_multigraph(events: list) -> bool:
    """ Returns ``True`` if events correspond to a graph. List of events corresponds to a graph if
    it is a list of 3-tuples or 4-tuples with the last element being an integer ``(-1, 1)``
    or a non-negative float.

    If events are 3-tuples, returns ``True`` if there are multiple events between the same pair of
    nodes. If events are 4-tuples, returns ``True`` if there are multiple events between the same
    pair of nodes or if any event has a duration (i.e., a non-zero float value for the last tuple
    element).

    :param list events: List of 3-tuple or 4-tuple edge-level events.
    """
    # (u, v, t)
    if len(events[0]) == 3:
        is_multigraph = 1 != max(Counter((tuple(e[:2]) for e in events)).values())
    # (u, v, t, e), where e is an integer in (-1, 1)
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
        is_multigraph = any(
            len(ranges) > 1 or len(ranges[0]) > 1 for ranges in temporal_edges.values())
    # (u, v, t, e), where e is a (non-negative) float defining the duration of the interaction
    elif len(events[0]) == 4 and type(events[0][-1]) == float:
        is_multigraph = any(
            e[-1] > 0 for e in events) or 1 != max(Counter((e[:2] for e in events)).values())
    return is_multigraph


def is_frozen(TG: Union[TemporalGraph, StaticGraph]) -> bool:
    """ Returns ``True`` if graph is frozen.

    A frozen graph is immutable, meaning that nodes and edges cannot be added or removed.
    Calling ``copy`` on a frozen graph returns a (mutable) deep copy of the graph object.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    """
    if not is_temporal_graph(TG) and not is_static_graph(TG):
        raise TypeError("Argument `graph` must be a temporal graph or a static graph.")
    if is_static_graph(TG):
        return nx.is_frozen(TG)
    return all([nx.is_frozen(G) for G in TG])


def is_static_graph(obj: Any) -> bool:
    """ Returns ``True`` if object is a static graph.

    Matches any of: NetworkX
    `Graph <https://networkx.org/documentation/stable/reference/classes/graph.html>`__,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__,
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__.

    :param obj: Object to check.
    """
    return (
        isinstance(obj, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph))
        and not is_temporal_graph(obj)
    )


def is_temporal_graph(obj: Any) -> bool:
    """ Returns ``True`` if object is a temporal graph.

    Matches any of:
    :class:`~networkx_temporal.classes.TemporalGraph`,
    :class:`~networkx_temporal.classes.TemporalDiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiDiGraph`.

    :param obj: Object to check.
    """
    from . import (
        TemporalABC, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    )
    return isinstance(obj, (
        TemporalABC, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph)
    )


def is_unrolled_graph(UTG: StaticGraph) -> bool:
    """ Returns ``True`` if static graph is an unrolled temporal graph.

    Unrolled graphs are a static representation of temporal networks, where each node is suffixed
    with its temporal index (e.g., ``'a_0'``) and inter-slice edges are added to connect copies of
    the same node at different time steps (e.g., ``'a_0'`` and ``'a_1'``).

    :param object UTG: Static graph object.
    """
    if not is_static_graph(UTG):
        raise False

    for node in UTG.nodes():
        if "_" not in str(node):
            return False
        _, t = str(node).rsplit("_", 1)
        if not t.isdigit():
            return False

    return True
