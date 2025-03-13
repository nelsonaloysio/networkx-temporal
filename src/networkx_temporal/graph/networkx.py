from functools import reduce, wraps
from operator import or_
from typing import Any, Callable, Optional, Union

import networkx as nx
from networkx.exception import NetworkXError

from ..typing import TemporalGraph
from ..utils import _dict, _sum


def decorate(cls: TemporalGraph, name: str) -> Callable:
    """
    Decorate methods inherited from a static NetworkX graph.

    :param self: Temporal graph object.
    :param name: Method name to decorate.
    """
    @wraps(getattr(cls[0], name))
    def wrapper(*args, **kwargs):
        returns = list(G.__getattribute__(name)(*args, **kwargs) for G in cls)
        if all(r is None for r in returns):
            return None
        if all(r is True for r in returns):
            return True
        if all(r is False for r in returns):
            return False
        return returns
    return wrapper


@wraps(nx.Graph.copy)
def copy(self, as_view: bool = False) -> TemporalGraph:
    from . import temporal_graph
    TG = temporal_graph(directed=self.is_directed(), multigraph=self.is_multigraph())
    TG.data = [G.copy(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG


@wraps(nx.Graph.degree)
def degree(self, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return __static_degree(self, "degree", nbunch=nbunch, weight=weight)


@wraps(nx.DiGraph.in_degree)
def in_degree(self, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return __static_degree(self, "in_degree", nbunch=nbunch, weight=weight)


@wraps(nx.Graph.neighbors)
def neighbors(self, node: Any) -> list:
    yield from [list(G.neighbors(node)) if G.has_node(node) else [] for G in self]


@wraps(nx.DiGraph.out_degree)
def out_degree(self, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return __static_degree(self, "out_degree", nbunch=nbunch, weight=weight)


@wraps(nx.Graph.to_directed)
def to_directed(self, as_view: Optional[bool] = True) -> TemporalGraph:
    assert as_view is None or type(as_view) == bool,\
        "Argument `as_view` must be either True or False."

    from . import temporal_graph
    TG = temporal_graph(directed=True, multigraph=self.is_multigraph())
    TG.data = [G.to_directed(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG


@wraps(nx.DiGraph.to_undirected)
def to_undirected(self, as_view: Optional[bool] = True) -> TemporalGraph:
    assert as_view is None or type(as_view) == bool,\
        "Argument `as_view` must be either True or False."

    from . import temporal_graph
    TG = temporal_graph(directed=False, multigraph=self.is_multigraph())
    TG.data = [G.to_undirected(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG


def _static_degree(self, degree: str, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    if nbunch is None:
        return [_dict(getattr(G, degree)(weight=weight)) for G in self]

    if not hasattr(nbunch, "__iter__"):
        if self.has_node(nbunch) is False:
            raise NetworkXError("nbunch is not a node or a sequence of nodes.")

        return [_dict(getattr(G, degree)(nbunch=nbunch, weight=weight))
                if G.has_node(nbunch) else None for i, G in enumerate(self)]

    return [_dict(getattr(G, degree)(nbunch=nbunch, weight=weight)) for G in self]
