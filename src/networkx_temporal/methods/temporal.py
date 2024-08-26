from functools import reduce
from operator import or_
from typing import Any

from .utils import reduce_sum


def is_temporal_graph(obj) -> bool:
    """
    Returns whether an object is a temporal graph.

    :param obj: Object to be tested.
    """
    from ..graph import TemporalBase
    return issubclass(type(obj), TemporalBase)


def temporal_degree(self, *args, **kwargs) -> dict:
    """ Returns degree of a node in all snapshots. """
    return reduce(reduce_sum, self.degree(*args, **kwargs))


def temporal_in_degree(self, *args, **kwargs) -> dict:
    """ Returns in-degree of a node in all snapshots. """
    return reduce(reduce_sum, self.in_degree(*args, **kwargs))


def temporal_out_degree(self, *args, **kwargs) -> dict:
    """ Returns out-degree of a node in all snapshots. """
    return reduce(reduce_sum, self.out_degree(*args, **kwargs))


def temporal_neighbors(self, node: Any) -> dict:
    """
    Returns neighbors of a node considering all snapshots.

    :param node: Node in the temporal graph.
    """
    return reduce(or_, iter(set(N) for N in self.neighbors(node)))


def temporal_nodes(self) -> list:
    """ Returns list of nodes in all snapshots. """
    return reduce(or_, self.nodes(data=False))


def temporal_edges(self) -> list:
    """ Returns list of edges (interactions) in all snapshots. """
    return list(e for E in self.edges() for e in E)


def temporal_order(self) -> int:
    """
    Returns number of temporal nodes.

    Matches the length of :func:`~networkx_temporal.TemporalGraph.temporal_nodes`.
    """
    return len(self.temporal_nodes())


def temporal_size(self) -> int:
    """
    Returns number of temporal edges (interactions).

    Matches the length of :func:`~networkx_temporal.TemporalGraph.temporal_edges`.
    """
    return len(self.temporal_edges())


def total_order(self) -> int:
    """
    Returns number of total nodes.

    Matches the sum of :func:`~networkx_temporal.TemporalGraph.order`.
    """
    return sum(self.order())


def total_size(self) -> int:
    """
    Returns number of total edges (interactions).

    Matches both the sum of :func:`~networkx_temporal.TemporalGraph.size` and
    the length of :func:`~networkx_temporal.TemporalGraph.temporal_edges`.
    """
    return sum(self.size())
