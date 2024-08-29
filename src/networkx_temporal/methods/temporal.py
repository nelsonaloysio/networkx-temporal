from functools import reduce
from operator import or_
from typing import Any, Optional, Union


def temporal_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
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
) -> Union[dict, int]:
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
) -> Union[dict, int]:
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
    Returns list of nodes (**without** duplicates) in all snapshots.
    """
    return list(set.union(*[set(G.nodes()) for G in self]))


def temporal_edges(self) -> list:
    """
    Returns list of edges (interactions) in all snapshots.
    """
    return list(e for G in self for e in G.edges())


def temporal_order(self) -> int:
    """
    Returns number of nodes (**without** duplicates) in all snapshots.

    Matches the length of :func:`~networkx_temporal.TemporalGraph.temporal_nodes`.
    """
    return len(self.temporal_nodes())


def temporal_size(self) -> int:
    """
    Returns number of edges (interactions) in all snapshots.

    Matches the length of :func:`~networkx_temporal.TemporalGraph.temporal_edges`.
    """
    return len(self.temporal_edges())


def total_order(self) -> int:
    """
    Returns number of nodes (with duplicates) in all snapshots.

    Matches the sum of :func:`~networkx_temporal.TemporalGraph.order`.
    """
    return sum(self.order())


def total_size(self) -> int:
    """
    Returns number of edges (interactions) in all snapshots.

    Matches both the sum of :func:`~networkx_temporal.TemporalGraph.size` and
    the length of :func:`~networkx_temporal.TemporalGraph.temporal_edges`.
    """
    return sum(self.size())


def reduce_sum(d1: Union[int, dict], d2: Union[int, dict]):
    """ Returns sum of two integers or dictionaries. """
    if type(d1) == int or type(d2) == int:
        return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)

    d1, d2 = dict(d1), dict(d2)
    return {v: d1.get(v, 0) + d2.get(v, 0) for v in set(d for d in {**d1, **d2})}


def to_dict(deg: Union[dict, int, float]) -> dict:
    """ Returns dictionary. """
    return dict(deg) if hasattr(deg, "__len__") else deg
