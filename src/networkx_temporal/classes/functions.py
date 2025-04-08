from functools import reduce
from operator import or_
from typing import Any

import networkx as nx

from ..typing import TemporalGraph


def all_neighbors(TG: TemporalGraph, node: Any) -> iter:
    """
    Returns iterator of all node neighbors in all snapshots. Does not consider edge direction.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param node: Node to get neighbors for.
    """
    yield from list(reduce(or_, iter(set(nx.all_neighbors(G, node)) for G in TG if G.has_node(node))))


def neighbors(TG: TemporalGraph, node: Any) -> iter:
    """
    Returns iterator of node neighbors in all snapshots. Considers edge direction.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param node: Node to get neighbors for.
    """
    yield from list(reduce(or_, iter(set(N) for N in TG.neighbors(node))))
