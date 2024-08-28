from functools import reduce
from operator import or_
from typing import Any, Optional, Union

from .utils import reduce_sum, to_dict


def is_temporal_graph(obj) -> bool:
    """
    Returns whether an object is a temporal graph.

    :param obj: Object to be tested.
    """
    from ..graph import TemporalBase
    return issubclass(type(obj), TemporalBase)


def temporal_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int, float]:
    """
    Returns node degrees considering all snapshots.

    :param: nbunch: One or more nodes to consider. Optional.
    :param: weight: Edge attribute key to consider. Optional.
    """
    return to_dict(reduce(reduce_sum, self.degree(nbunch=nbunch, weight=weight)))


def temporal_in_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int, float]:
    """
    Returns node in-degrees considering all snapshots.

    :param: nbunch: One or more nodes to consider. Optional.
    :param: weight: Edge attribute key to consider. Optional.
    """
    return to_dict(reduce(reduce_sum, self.in_degree(nbunch=nbunch, weight=weight)))


def temporal_out_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int, float]:
    """
    Returns node out-degrees considering all snapshots.

    :param: nbunch: One or more nodes to consider. Optional.
    :param: weight: Edge attribute key to consider. Optional.
    """
    return to_dict(reduce(reduce_sum, self.out_degree(nbunch=nbunch, weight=weight)))


def temporal_neighbors(self, node: Any) -> list:
    """
    Returns list of node neighbors in all snapshots.

    :param node: Node in the temporal graph.
    """
    return list(reduce(or_, iter(set(N) for N in self.neighbors(node))))


def temporal_nodes(self) -> list:
    """
    Returns list of nodes in all snapshots.
    """
    return list(set.union(*[set(G.nodes()) for G in self]))


def temporal_edges(self) -> list:
    """
    Returns list of edges (interactions) in all snapshots.
    """
    return list(e for G in self for e in G.edges())


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
