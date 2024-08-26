from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalGraph(TemporalBase, nx.Graph):
    """
    Returns a :class:`~networkx_temporal.TemporalGraph` object
    initialized with ``directed=False`` and ``multigraph=False``.

    This class may optionally be used to create a temporal undirected graph.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=False)


class TemporalDiGraph(TemporalBase, nx.DiGraph):
    """
    Returns a :class:`~networkx_temporal.TemporalGraph` object
    initialized with ``directed=True`` and ``multigraph=False``.

    This class may optionally be used to create a temporal directed graph.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=True, multigraph=False)


class TemporalMultiGraph(TemporalBase, nx.MultiGraph):
    """
    Returns a :class:`~networkx_temporal.TemporalGraph` object
    initialized with ``directed=False`` and ``multigraph=True``.

    This class may optionally be used to create a temporal undirected multigraph.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=True)


class TemporalMultiDiGraph(TemporalBase, nx.MultiDiGraph):
    """
    Returns a :class:`~networkx_temporal.TemporalGraph` object
    initialized with ``directed=True`` and ``multigraph=True``.

    This class may optionally be used to create a temporal directed multigraph.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=True, multigraph=True)
