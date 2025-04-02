from typing import Optional


def order(self, copies: Optional[bool] = None) -> int:
    """
    Returns number of nodes in the temporal graph.
    Matches the length of :attr:`~networkx_temporal.Graph.temporal_nodes`
    if ``copies=False``:

    .. math::

        \\text{order} =
        \\begin{cases}
            [\\{G \\in \\mathcal{G}} |V|] & \\text{if \\texttt{copies} is \\texttt{None}} \\\\
            \\sum_{G \\in \\mathcal{G}} |V| & \\text{if \\texttt{copies} is \\texttt{True}} \\\\
            |\\mathcal{V}| & \\text{otherwise,}
        \\end{cases}

    where :math:`|\\mathcal{V}|` is the number of nodes in the temporal graph :math:`\\mathcal{G}`,
    and :math:`|V|` is the number of nodes in a snapshot :math:`G \\in \\mathcal{G}`.

    :param copies: Controls whether to count multiple instances of the same node in different
        snapshots. If ``True``, count multiple instances. If ``False``, count only unique nodes.
        If ``None`` (default), return list of node counts for each snapshot.

    """
    if copies is None:
        return [G.order() for G in self]
    if copies is True:
        return sum(G.order() for G in self)
    if copies is False:
        return len(self.temporal_nodes())
    raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")


def size(self, copies: Optional[bool] = None) -> int:
    """
    Returns number of edges (interactions).
    Matches the length of :attr:`~networkx_temporal.Graph.temporal_edges`
    if ``copies=True``:

    .. math::

        \\text{size} =
        \\begin{cases}
            \\{G \\in \\mathcal{G}} |E|] & \\text{if \\texttt{copies} is \\texttt{None}} \\\\
            \\bigcup_{G \\in \\mathcal{G}} |E| & \\text{if \\texttt{copies} is \\texttt{False}} \\\\
            |\\mathcal{E}| & \\text{otherwise,}
        \\end{cases}

    where :math:`|\\mathcal{E}|` is the number of nodes in the temporal graph :math:`\\mathcal{G}`,
    and :math:`|V|` is the number of edges in a snapshot :math:`G \\in \\mathcal{G}`.

    :param copies: If ``True``, consider multiple instances of the same edge in different
        snapshots. If ``False``, consider only unique edges. Default is ``None``.
    """
    if copies is None:
        return [G.size() for G in self]
    if copies is True:
        return len(self.temporal_edges())
    if copies is False:
        return len(set(self.temporal_edges()))
    raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")
