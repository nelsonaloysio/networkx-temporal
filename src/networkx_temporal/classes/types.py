from typing import Any, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


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
