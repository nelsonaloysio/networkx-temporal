from ..typing import TemporalGraph
from functools import reduce, wraps
from operator import or_
from typing import Any, Callable, Optional, Union

import networkx as nx

from ..typing import Literal, TemporalGraph


def wrapper(self: TemporalGraph, name: str) -> Callable:
    """
    Return a wrapper function for methods inherited from a static NetworkX graph.

    This wrapper function is used to handle the case where the method returns
    different booleans for different graphs in the temporal graph. It combines
    the results from all graphs in the temporal graph and returns a single result.
    Otherwise, it returns a list of results from each graph in the temporal graph.

    :param cls: Temporal graph class.
    :param name: Method name to decorate.
    """
    @wraps(getattr(self[0], name))
    def _wrapper(*args, **kwargs):
        returns = list(G.__getattribute__(name)(*args, **kwargs) for G in self)
        if all(r is None for r in returns):
            return None
        if all(r is True for r in returns):
            return True
        if all(r is False for r in returns):
            return False
        return returns
    return _wrapper


@wraps(nx.all_neighbors)
def all_neighbors(self: TemporalGraph, node: Any) -> iter:
    yield from list(
        reduce(or_, iter(set(nx.all_neighbors(G, node)) for G in self if G.has_node(node))))
all_neighbors.__doc__ += "\n:meta private:"


@wraps(nx.Graph.copy)
def copy(self: TemporalGraph, as_view: bool = False) -> TemporalGraph:
    from . import temporal_graph
    TG = temporal_graph(directed=self.is_directed(), multigraph=self.is_multigraph())
    TG.data = [G.copy(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG
copy.__doc__ += "\n:meta private:"


@wraps(nx.Graph.degree)
def degree(self: TemporalGraph, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return _degree(self, "degree", nbunch=nbunch, weight=weight)
degree.__doc__ += "\n:meta private:"


# NOTE: @wraps(nx.DiGraph.in_degree): ERROR: Unexpected indentation (sphinx docstring).
@wraps(nx.Graph.degree)
def in_degree(self: TemporalGraph, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return _degree(self, "in_degree", nbunch=nbunch, weight=weight)
in_degree.__doc__ += "\n:meta private:"


@wraps(nx.Graph.neighbors)
def neighbors(self: TemporalGraph, node: Any) -> iter:
    yield from list(
        reduce(or_, iter(set(N) for N in self.neighbors(node))))
neighbors.__doc__ += "\n:meta private:"


# NOTE: @wraps(nx.DiGraph.out_degree): ERROR: Unexpected indentation (sphinx docstring).
@wraps(nx.Graph.degree)
def out_degree(self: TemporalGraph, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return _degree(self, "out_degree", nbunch=nbunch, weight=weight)
out_degree.__doc__ += "\n:meta private:"


@wraps(nx.Graph.to_directed)
def to_directed(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    assert as_view is None or type(as_view) == bool,\
        "Argument `as_view` must be either True or False."
    from . import temporal_graph
    TG = temporal_graph(directed=True, multigraph=self.is_multigraph())
    TG.data = [G.to_directed(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG
to_directed.__doc__ += "\n:meta private:"


@wraps(nx.DiGraph.to_undirected)
def to_undirected(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    assert as_view is None or type(as_view) == bool,\
        "Argument `as_view` must be either True or False."
    from . import temporal_graph
    TG = temporal_graph(directed=False, multigraph=self.is_multigraph())
    TG.data = [G.to_undirected(as_view=as_view) for G in self]
    TG.name = self.name
    TG.names = self.names
    return TG
to_undirected.__doc__ += "\n:meta private:"


def _degree(
    self: TemporalGraph,
    degree: Literal["degree", "in_degree", "out_degree"],
    nbunch: Any = None,
    weight: str = None,
) -> Union[dict, int]:

    assert degree in ("degree", "in_degree", "out_degree"),\
        f"Argument `degree` must be one of ('degree', 'in_degree', 'out_degree')."

    degrees = [getattr(G, degree)(nbunch=nbunch, weight=weight) for G in self]

    if nbunch is None or isinstance(nbunch, (list, tuple)):
        return [dict(d) for d in degrees]

    return [d if type(d) == int else None for d in degrees]
