from typing import Optional

from .base import TemporalBase


class TemporalGraph(TemporalBase):
    """
    Temporal graph with undirected edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=False, multigraph=False)


class TemporalDiGraph(TemporalBase):
    """
    Temporal graph with directed edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=True, multigraph=False)


class TemporalMultiGraph(TemporalBase):
    """
    Temporal graph with multiple undirected edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=False, multigraph=True)


class TemporalMultiDiGraph(TemporalBase):
    """
    Temporal graph with multiple directed edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=True, multigraph=True)

