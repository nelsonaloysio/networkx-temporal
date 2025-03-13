from warnings import warn


def order(self, copies: bool = False) -> int:
    """
    Returns number of nodes. Matches the length of
    :func:`~networkx_temporal.graph.TemporalGraph.temporal_nodes`
    if ``copies=False``, i.e.,

    .. math::

        \\text{order} =
        \\begin{cases}
            \\sum_{G \\in \\mathcal{G}} |V| & \\text{if \\texttt{copies} is \\texttt{True}} \\\\
            |\\mathcal{V}| & \\text{otherwise,}
        \\end{cases}

    where :math:`|\\mathcal{V}|` is the number of nodes in the temporal graph :math:`\\mathcal{G}`,
    and :math:`|V|` is the number of nodes in a snapshot :math:`G \\in \\mathcal{G}`. Both are
    equivalent if :func:`~networkx_temporal.graph.TemporalGraph.flatten` is called on the
    :class:`~networkx_temporal.graph.TemporalGraph` beforehand.

    :param copies: If ``True``, consider multiple instances of the same node in different
        snapshots. Default is ``False``.

    :note: Equivalent to the method :func:`~networkx_temporal.graph.TemporalGraph.total_order`
        in :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    return sum(self.order()) if copies else len(self.temporal_nodes())


def size(self) -> int:
    """
    Returns number of edges (interactions). Matches the length of
    :func:`~networkx_temporal.graph.TemporalGraph.temporal_edges`:

    .. math::

        \\text{size} = |\\mathcal{E}| = \\sum_{G \\in \\mathcal{G}} |E|,

    where :math:`\\mathcal{E}` are edges in the temporal graph :math:`\\mathcal{G}`,
    and :math:`|E|` are edges in a snapshot :math:`G \\in \\mathcal{G}`.

    :note: Equivalent to the method :func:`~networkx_temporal.graph.TemporalGraph.total_size`
        in :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    return len(self.temporal_edges())


def _temporal_order(self) -> int:
    """
    Deprecated in favor of :func:`networkx_temporal.graph.base.total_order`.

    :meta private:
    """
    warn("Function `temporal_order` deprecated in favor of `total_order(copies=False)`.")
    return self.total_order(copies=False)


def _temporal_size(self) -> int:
    """
    Deprecated in favor of :func:`networkx_temporal.graph.base.total_size`.

    :meta private:
    """
    warn("Function `temporal_size` deprecated in favor of `total_size`.")
    return self.total_size()
