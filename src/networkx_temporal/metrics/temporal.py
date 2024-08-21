from functools import reduce
from operator import or_
from typing import Any

from .utils import reduce_sum


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
    """ Returns all nodes in all snapshots. """
    return reduce(or_, self.nodes(data=False))


def temporal_edges(self) -> list:
    """ Returns all edges in all snapshots. """
    return list(e for E in self.edges() for e in E)


def temporal_order(self) -> int:
    """ Returns total number of nodes (without duplicates) in the temporal graph. """
    return len(self.temporal_nodes())


def temporal_size(self) -> int:
    """ Returns total number of edges in the temporal graph. Same as ``total_edges``."""
    return sum(self.size())
