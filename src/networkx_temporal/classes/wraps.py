from ..typing import TemporalGraph
from functools import reduce, wraps
from operator import or_
from typing import Any, Callable, Optional, Union

import networkx as nx
from networkx.exception import NetworkXError

from ..typing import Literal, TemporalGraph, StaticGraph


def wrapper(TG: TemporalGraph, G: StaticGraph, name: str) -> Callable:
    """ Return a wrapper function for methods inherited from a static NetworkX graph.

    If the output of a function decorated by this wrapper is a list of booleans
    or None values, returns a single boolean or None value instead. This wrapper
    is used to decorate NetworkX inherited functions for graph snapshots.

    :param cls: Temporal graph class.
    :param name: Method name to decorate.
    """
    @wraps(getattr(G, name))
    def _wrapper(*args, **kwargs):
        returns = list(G.__getattribute__(name)(*args, **kwargs) for G in TG)
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
    yield from iter(
        list(set(nx.all_neighbors(G, node))) if G.has_node(node) else [] for G in self
    )
all_neighbors.__doc__ += "\n:meta private:"

@wraps(nx.Graph.neighbors)
def neighbors(self: TemporalGraph, node: Any) -> iter:
    yield from iter(
        list(set(nx.neighbors(G, node))) if G.has_node(node) else [] for G in self
    )
neighbors.__doc__ += "\n:meta private:"


@wraps(nx.Graph.copy)
def copy(self: TemporalGraph, as_view: bool = False) -> TemporalGraph:
    TG = self.__class__(t=0)
    TG.add_snapshots_from([G.copy(as_view=as_view) for G in self])
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

# NOTE: @wraps(nx.DiGraph.out_degree): ERROR: Unexpected indentation (sphinx docstring).
@wraps(nx.Graph.degree)
def out_degree(self: TemporalGraph, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
    return _degree(self, "out_degree", nbunch=nbunch, weight=weight)
out_degree.__doc__ += "\n:meta private:"


@wraps(nx.Graph.to_directed)
def to_directed(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    if as_view is not None and type(as_view) != bool:
        raise TypeError("Argument `as_view` must be either True or False.")
    from . import TemporalDiGraph, TemporalMultiDiGraph
    TG = TemporalMultiDiGraph(t=0) if self.is_multigraph() else TemporalDiGraph(t=0)
    TG.add_snapshots_from([G.to_directed(as_view=as_view) for G in self])
    TG.name = self.name
    TG.names = self.names
    return TG
to_directed.__doc__ += "\n:meta private:"


@wraps(nx.DiGraph.to_undirected)
def to_undirected(self: TemporalGraph, as_view: Optional[bool] = True) -> TemporalGraph:
    if as_view is not None and type(as_view) != bool:
        raise TypeError("Argument `as_view` must be either True or False.")
    from . import TemporalGraph, TemporalMultiGraph
    TG = TemporalMultiGraph(t=0) if self.is_multigraph() else TemporalGraph(t=0)
    TG.add_snapshots_from([G.to_undirected(as_view=as_view) for G in self])
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

    if degree not in ("degree", "in_degree", "out_degree"):
        raise ValueError("Argument `degree` not in ('degree', 'in_degree', 'out_degree').")

    def _degree_view(G: nx.Graph) -> nx.classes.reportviews.DegreeView:
        # Avoid raising exception when `nbunch` is a node (e.g., an int) not in `G`.
        try:
            return getattr(G, degree)(nbunch=nbunch, weight=weight)
        except NetworkXError:
            return getattr(G, degree)(nbunch=[], weight=weight)

    degrees = [_degree_view(G) for G in self]
    if nbunch is None or isinstance(nbunch, (list, tuple)):
        return degrees
    return [d if type(d) == int else None for d in degrees]
