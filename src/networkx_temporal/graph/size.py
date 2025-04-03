from typing import Optional


def size(self, copies: Optional[bool] = None) -> int:
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

        Matches the length of :func:`~networkx_temporal.graph.TemporalGraph.temporal_edges`
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
