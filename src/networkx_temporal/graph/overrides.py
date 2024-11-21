from typing import Any

from ..typing import TemporalGraph


def _copy(TG: TemporalGraph) -> TemporalGraph:
    """
    Returns a deep copy of the temporal graph.

    Overrides the default behavior of ``networkx.Graph.copy`` to return a
    :class:`~networkx_temporal.graph.TemporalGraph` object instead of a list of graph objects.

    :meta private:
    """
    TG.data = [G.copy() for G in TG]
    return TG


def _is_directed(TG: TemporalGraph, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is directed, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_directed() for G in TG] if on_each else TG[0].is_directed()


def _is_multigraph(TG: TemporalGraph, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is a multigraph, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_multigraph() for G in TG] if on_each else TG[0].is_multigraph()


def _neighbors(TG: TemporalGraph, node: Any) -> list:
    """
    Returns neighbors of a node for each snapshot.

    Overrides the default behavior of ``networkx.Graph.neighbors`` to return an empty
    list if the node is not present in the snapshot, instead of raising an exception.

    :param node: Node in the temporal graph.

    :meta private:
    """
    return list(list(G.neighbors(node)) if G.has_node(node) else [] for G in TG)


def _to_directed(TG: TemporalGraph, as_view: bool = True) -> TemporalGraph:
    """
    Returns directed version of temporal graph.

    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.
    """
    assert type(as_view) == bool,\
        f"Argument 'as_view' must be either True or False."

    TG.data = [G.to_directed(as_view=as_view) for G in TG]
    return TG


def _to_undirected(TG: TemporalGraph, as_view: bool = True) -> TemporalGraph:
    """
    Returns undirected version of temporal graph.

    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.
    """
    assert type(as_view) == bool,\
        f"Argument 'as_view' must be either True or False."

    TG.data = [G.to_undirected(as_view=as_view) for G in TG]
    return TG
