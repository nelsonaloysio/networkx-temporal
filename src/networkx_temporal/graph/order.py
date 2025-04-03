from typing import Optional


def order(self, copies: Optional[bool] = None) -> int:
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

        Matches the length of :func:`~networkx_temporal.graph.TemporalGraph.temporal_nodes`
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

