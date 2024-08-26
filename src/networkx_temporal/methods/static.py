from typing import Any

from ..typing import TemporalGraph


def neighbors(self, node: Any) -> list:
    """
    Returns neighbors of a node considering each snapshot.

    :param node: Node in the temporal graph.

    :meta private:
    """
    return list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)


def is_directed(self, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is directed, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_directed() for G in self] if on_each else self[0].is_directed()


def is_multigraph(self, on_each: bool = False) -> bool:
    """
    Returns ``True`` if the graph is a multigraph, ``False`` otherwise.

    Obtains the value from the first snapshot only, unless ``on_each=True``.

    :param bool on_each: If ``True``, checks all snapshots for the graph type.
    """
    return [G.is_multigraph() for G in self] if on_each else self[0].is_multigraph()


def to_directed(self, as_view: bool = True) -> TemporalGraph:
    """
    Returns directed version of temporal graph.

    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.

    :meta private:
    """
    assert type(as_view) == bool,\
        f"Argument 'as_view' must be either True or False."

    if as_view is False:
        self.data = [G.to_directed(as_view=as_view) for G in self]
        return self

    from ..graph import temporal_graph
    TG = temporal_graph(directed=True, multigraph=self.is_multigraph())
    TG.data = [G.to_directed() for G in self]
    return TG


def to_undirected(self, as_view: bool = True) -> TemporalGraph:
    """
    Returns undirected version of temporal graph.

    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.

    :meta private:
    """
    assert type(as_view) == bool,\
        f"Argument 'as_view' must be either True or False."

    if as_view is False:
        self.data = [G.to_undirected(as_view=as_view) for G in self]
        return self

    from ..graph import temporal_graph
    TG = temporal_graph(directed=False, multigraph=self.is_multigraph())
    TG.data = [G.to_undirected() for G in self]
    return TG
