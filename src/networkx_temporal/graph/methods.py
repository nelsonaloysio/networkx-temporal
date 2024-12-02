from typing import Any, Optional

from ..typing import TemporalGraph


def _copy(self: TemporalGraph) -> TemporalGraph:
    """
    Returns a deep copy of the temporal graph.

    Overrides the default behavior of ``networkx.Graph.copy`` to return a
    :class:`~networkx_temporal.graph.TemporalGraph` object instead of a list of graph objects.

    :meta private:
    """
    self.data = [G.copy() for G in self]
    return self


def _is_directed(self: TemporalGraph, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is directed, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param self: Temporal graph object.
    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_directed() for G in self] if on_each else self[0].is_directed()


def _is_multigraph(self: TemporalGraph, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is a multigraph, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param self: Temporal graph object.
    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_multigraph() for G in self] if on_each else self[0].is_multigraph()


def _neighbors(self: TemporalGraph, node: Any) -> list:
    """
    Returns neighbors of a node for each snapshot.

    Overrides the default behavior of ``networkx.Graph.neighbors`` to return an empty
    list if the node is not present in the snapshot, instead of raising an exception.

    :param node: Node in the temporal graph.

    :meta private:
    """
    return list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)


def _to_directed(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    """
    Returns directed version of temporal graph.

    :param self: Temporal graph object.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.
    """
    assert as_view is None or type(as_view) == bool,\
        "Argument 'as_view' must be either True or False."

    from . import temporal_graph
    TG = temporal_graph(directed=True, multigraph=self.is_multigraph())
    TG.data = [G.to_directed(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG


def _to_undirected(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    """
    Returns undirected version of temporal graph.

    :param self: Temporal graph object.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.
    """
    assert as_view is None or type(as_view) == bool,\
        "Argument 'as_view' must be either True or False."

    from . import temporal_graph
    TG = temporal_graph(directed=False, multigraph=self.is_multigraph())
    TG.data = [G.to_undirected(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG
