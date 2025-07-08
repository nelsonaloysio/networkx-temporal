from functools import reduce
from typing import Any, Optional

import networkx as nx

from ..typing import TemporalGraph


def all_neighbors(self: TemporalGraph, node: Any) -> iter:
    """
    Returns iterator of node neighbors for each snapshot. Does not consider edge direction.

    :param node: Node to get neighbors for.
    """
    yield from list(list(nx.all_neighbors(G, node)) if G.has_node(node) else [] for G in self)


def neighbors(self: TemporalGraph, node: Any) -> iter:
    """
    Returns iterator of node neighbors for each snapshot. Considers edge direction.

    :param node: Node to get neighbors for.
    """
    yield from list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)


def order(self: TemporalGraph, copies: Optional[bool] = None) -> int:
    """
    Returns number of nodes in the temporal graph.

    The argument ``copies`` determines how multiple nodes are counted:

    - If ``True``, returns the sum of the number of nodes in each snapshot.
    - If ``False``, returns the number of unique nodes across all snapshots.
    - If ``None``, returns the number of nodes in each snapshot (default).

    The order of a temporal graph is therefore equivalent to:

    .. math::

        \\text{order}(\\mathcal{G}) =
        \\begin{cases}
            \\bigcup_{G \\in \\mathcal{G}} |V| & \\text{if } \\texttt{copies} \\text{ is } \\texttt{False} \\\\
            \\sum_{G \\in \\mathcal{G}} |V| & \\text{if } \\texttt{copies} \\text{ is } \\texttt{True} \\\\
            \\forall_{G \\in \\mathcal{G}} \\, |V| & \\text{otherwise,}
        \\end{cases}

    where
    :math:`\\mathcal{G}` is a temporal graph,
    :math:`G` is a snapshot,
    and :math:`|V|` is its number of nodes.

    .. note::

        Matches the length of :func:`~networkx_temporal.classes.TemporalGraph.temporal_nodes`
        if ``copies=False`` (consider each node once).

    :param copies: If ``True``, consider multiple instances of the same node in different
        snapshots. If ``False``, consider unique nodes. Optional.
    """
    if copies is None:
        return [G.order() for G in self]
    if copies is True:
        return sum(G.order() for G in self)
    if copies is False:
        return len(set(self.temporal_nodes()))
    raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")


def size(self: TemporalGraph, copies: Optional[bool] = None) -> int:
    """
    Returns number of edges in the temporal graph.

    The argument ``copies`` determines how multiple edges are counted:

    - If ``True``, returns the sum of the number of edges in each snapshot.
    - If ``False``, returns the number of unique edges across all snapshots.
    - If ``None``, returns the number of edges in each snapshot (default).

    The size of a temporal graph is therefore equivalent to:

    .. math::

        \\text{size}(\\mathcal{G}) =
        \\begin{cases}
            \\sum_{G \\in \\mathcal{G}} |E| & \\text{if } \\texttt{copies} \\text{ is } \\texttt{True} \\\\
            \\bigcup_{G \\in \\mathcal{G}} |E| & \\text{if } \\texttt{copies} \\text{ is } \\texttt{False} \\\\
            \\forall_{G \\in \\mathcal{G}} \\, |E| & \\text{otherwise,}
        \\end{cases}

    where
    :math:`\\mathcal{G}` is a temporal graph,
    :math:`G` is a snapshot,
    and :math:`|E|` is its number of edges.

    .. note::

        Matches the length of :func:`~networkx_temporal.classes.TemporalGraph.temporal_edges`
        if ``copies=True`` (consider all node interactions).

    :param copies: If ``True``, consider multiple instances of the same edge in different
        snapshots. If ``False``, consider unique edges. Optional.
    """
    if copies is None:
        return [G.size() for G in self]
    if copies is True:
        return sum(G.size() for G in self)
    if copies is False:
        return len(set(self.temporal_edges()))
    raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")


def temporal_edges(self: TemporalGraph, copies: Optional[bool] = None, *args, **kwargs) -> list:
    """
    Returns list of edges (interactions) in all snapshots.

    :param copies: If ``True``, consider multiple instances of the same edge in different
        snapshots. Default is ``True``.
    :param args: Additional arguments to pass to the NetworkX graph method.
    :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
    """
    if copies is False:
        return reduce(lambda x, y: x.union(y), [set(G.edges(*args, **kwargs)) for G in self])
    return list(e for G in self for e in G.edges(*args, **kwargs))


def temporal_nodes(self: TemporalGraph, copies: Optional[bool] = None, *args, **kwargs) -> list:
    """
    Returns list of nodes in all snapshots.

    :param copies: If ``True``, consider multiple instances of the same node in different
        snapshots. Default is ``False``.
    :param args: Additional arguments to pass to the NetworkX graph method.
    :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
    """
    copies = False if copies is None else copies
    if copies is False:
        return reduce(lambda x, y: x.union(y), [set(G.nodes(*args, **kwargs)) for G in self])
    return list(e for G in self for e in G.nodes(*args, **kwargs))


def temporal_order(self: TemporalGraph) -> int:
    """
    Return number of unique nodes in all snapshots.
    Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=False``.

    .. seealso::

        The :func:`~networkx_temporal.classes.TemporalGraph.total_order` method for the sum of
        the number of nodes in all snapshots.
    """
    return self.order(copies=False)


def temporal_size(self: TemporalGraph) -> int:
    """
    Return number of unique edges in all snapshots.
    Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=False``.

    .. seealso::

        The :func:`~networkx_temporal.classes.TemporalGraph.total_order` method for the sum of
        the number of edges in all snapshots.
    """
    return self.size(copies=False)


def total_order(self: TemporalGraph) -> int:
    """
    Return sum of nodes from all snapshots.
    Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=True``.

    .. seealso::

        The :func:`~networkx_temporal.classes.TemporalGraph.temporal_order` method for the
        number of unique nodes in the temporal graph.
    """
    return self.order(copies=True)


def total_size(self: TemporalGraph) -> int:
    """
    Return sum of edges from all snapshots.
    Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=True``.

    .. seealso::

        The :func:`~networkx_temporal.classes.TemporalGraph.temporal_size` method for the
        number of unique edges in the temporal graph.
    """
    return self.size(copies=True)
