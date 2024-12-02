from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional, Union
from warnings import warn

import networkx as nx

from .methods import (
    _copy,
    _is_directed,
    _is_multigraph,
    _neighbors,
    _to_directed,
    _to_undirected
)
from .slice import slice
from ..metrics import (
    temporal_degree,
    temporal_in_degree,
    temporal_out_degree,
    temporal_neighbors,
    temporal_nodes,
    temporal_edges,
    temporal_order,
    temporal_size,
    total_order,
    total_size
)
from ..transform import (
    to_events,
    to_snapshots,
    to_static,
    to_unified
)
from ..typing import StaticGraph, TemporalGraph
from ..utils.convert import convert


class TemporalBase(metaclass=ABCMeta):
    """
    Base class for temporal graphs.

    This class is not meant to be instantiated directly, but is rather inherited by the classes
    :class:`~networkx_temporal.graph.TemporalGraph`,
    :class:`~networkx_temporal.graph.TemporalDiGraph`,
    :class:`~networkx_temporal.graph.TemporalMultiGraph`,
    and :class:`~networkx_temporal.graph.TemporalMultiDiGraph`.
    """
    convert = convert
    slice = slice
    temporal_degree = temporal_degree
    temporal_in_degree = temporal_in_degree
    temporal_out_degree = temporal_out_degree
    temporal_neighbors = temporal_neighbors
    temporal_nodes = temporal_nodes
    temporal_edges = temporal_edges
    temporal_order = temporal_order
    temporal_size = temporal_size
    total_order = total_order
    total_size = total_size

    # Static methods; override NetworkX methods.
    copy = _copy
    neighbors = _neighbors
    is_directed = _is_directed
    is_multigraph = _is_multigraph
    to_directed = _to_directed
    to_undirected = _to_undirected

    # Transform methods.
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    @abstractmethod
    def __init__(self, t: Optional[int] = None, directed: bool = None, multigraph: bool = None):
        graph = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")
        self.data = [graph() for _ in range(t or 1)]
        _wrapper_networkx(self, graph)

    def __getitem__(self, t: Union[str, int, slice]) -> StaticGraph:
        """ Returns snapshot from a given interval. """
        assert self.data,\
            "Temporal graph is empty."

        assert type(t) != str or self.names,\
            "Temporal graph snapshots are not named."

        assert type(t) != int or -len(self) <= t < len(self),\
            f"Received index {t}, but temporal graph has {len(self)} snapshots."

        assert type(t) != slice or -len(self) <= (t.start or 0) < (t.stop or len(self)) <= len(self),\
            f"Received slice {t.start, t.stop}, but temporal graph has {len(self)} snapshots."

        if type(t) == str:
            return self.data[self.names.index(t)]

        if type(t) == int:
            return self.data[t]

        from . import temporal_graph
        TG = temporal_graph(directed=self.is_directed(), multigraph=self.is_multigraph())
        TG.data = self.data[t]
        return TG

    def __iter__(self) -> iter:
        """ Returns iterator over slices in the temporal graph. """
        return iter(self.data)

    def __len__(self) -> int:
        """ Returns number of slices in the temporal graph. """
        return len(self.data)

    def __str__(self) -> str:
        """ Returns string representation of the class. """
        return f"Temporal"\
               f"{'Multi' if self.is_multigraph() else ''}"\
               f"{'Di' if self.is_directed() else ''}"\
               f"Graph (t={len(self)}) "\
               f"with {self.temporal_order()} nodes and {self.temporal_size()} edges"

    @property
    def data(self) -> list:
        """
        The ``data`` property of the temporal graph.

        :getter: Returns temporal graph data.
        :setter: Sets temporal graph data. Accepts a list, tuple, or dictionary of NetworkX graphs.
            Passing a dictionary will set the ``names`` property to its keys.
        :rtype: list
        """
        return self.__dict__.get("_data", None)

    @data.setter
    def data(self, data: Union[StaticGraph, dict, list, tuple]):
        """
        Setter for the ``data`` property of the temporal graph.
        """
        if type(data) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
            data = [data]

        assert type(data) in (dict, list, tuple),\
            f"Argument 'data' must be a NetworkX graph or list of graphs, received: {type(data)}."

        names = list(data.keys()) if type(data) == dict else None
        data = list(data.values() if type(data) == dict else data)

        assert all(type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for G in data),\
            "All elements in data must be valid NetworkX graphs."

        self._data = data
        self.names = names

    @property
    def name(self) -> str:
        """
        The ``name`` property of the temporal graph.

        :getter: Returns temporal graph name.
        :setter: Sets temporal graph name.
        :rtype: str
        """
        return self.__dict__.get("_name", "")

    @name.setter
    def name(self, name: Any):
        """
        Setter for the ``name`` property of the temporal graph.
        """
        self.__dict__.pop("_name", None) if name is None else self.__setattr__("_name", name)

    @property
    def names(self) -> list:
        """
        The ``names`` property of the temporal graph. Used to store temporal intervals on
        :func:`~networkx_temporal.graph.TemporalGraph.slice`.

        :getter: Returns names of temporal graph snapshots.
        :setter: Sets names of temporal graph snapshots.
        :rtype: list
        """
        return self.__dict__.get("_names", None)

    @names.setter
    def names(self, names: Optional[Union[list, tuple]]):
        """
        Setter for the ``names`` property of the temporal graph.
        """
        assert names is None or type(names) in (list, tuple),\
            f"Argument 'names' must be a list or tuple, received: {type(names)}."

        assert names is None or len(names) == len(self),\
            f"Length of names ({len(names)}) differs from number of snapshots ({len(self)})."

        assert names is None or all(type(n) in (str, int) and type(n) == type(names[0]) for n in names),\
            "All elements in names must be either strings or integers."

        assert names is None or len(names) == len(set(names)),\
            "All elements in names must be unique."

        # NOTE: Does not work if graphs are views, as setting one view will set all objects.
        # list(setattr(self[t], "name", names[t]) for t in range(len(self)))

        self.__dict__.pop("_names", None) if names is None else self.__setattr__("_names", names)

    def append(self, G: Optional[StaticGraph] = None) -> None:
        """
        Appends a new snapshot to the temporal graph.

        :param G: NetworkX graph object to append. Optional.
        """
        self.insert(len(self), G)

    def flatten(self) -> TemporalGraph:
        """
        Returns ''flattened'' version of temporal graph.
        Equivalent to :func:`~networkx_temporal.graph.TemporalGraph.slice` with ``bins=1``.

        This method differs from :func:`~networkx_temporal.graph.TemporalGraph.to_static` only in the
        sense that it returns a :class:`~networkx_temporal.graph.TemporalGraph` object with a single
        snapshot, rather than a static NetworkX graph object.

        .. attention::

           As each node in a flattened graph is unique, dynamic node attributes are not preserved.
        """
        return self.slice(bins=1)

    def insert(self, index: int, G: Optional[StaticGraph] = None) -> None:
        """
        Inserts a new snapshot to the temporal graph at a given index.

        :param index: Insert graph object before index.
        :param G: NetworkX graph object to insert. Optional.
        """
        directed = self.is_directed()
        multigraph = self.is_multigraph()

        if G is None:
            G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()

        assert type(index) == int,\
            f"Argument `index` must be an integer, received: {type(index)}."

        assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
            f"Argument `G` must be a valid NetworkX graph, received: {type(G)}."

        assert G.is_directed() == directed,\
            f"Received a{' directed' if G.is_directed() else 'n undirected'} graph, "\
            f"but temporal graph is {'' if directed else 'un'}directed."

        assert G.is_multigraph() == multigraph,\
            f"Received a {'multi' if G.is_multigraph() else ''}graph, "\
            f"but temporal graph is {'' if multigraph else 'not '}a multigraph."

        self.data.insert(index, G)

    def index_edge(self, edge: tuple, interval: Optional[range] = None) -> list:
        """
        Returns index of all snapshots in which an edge is present.

        :param edge: Edge to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
            Accepts either a ``range`` or a ``tuple`` of integers.
        """
        assert interval is None or type(interval) in (range, tuple),\
            "Argument `interval` must be a range or tuple of integers."

        if interval is None:
            interval = range(len(self))

        elif type(interval) == tuple:
            interval = range(*interval)

        print(edge)
        return [i for i in (interval or range(len(self))) if self[i].has_edge(*edge)]

    def index_node(self, node: Any, interval: Optional[range] = None) -> list:
        """
        Returns index of all snapshots in which a node is present.

        :param node: Node to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
            Accepts either a ``range`` or a ``tuple`` of integers.
        """
        assert interval is None or type(interval) in (range, tuple),\
            "Argument `interval` must be a range or tuple of integers."

        if interval is None:
            interval = range(len(self))

        elif type(interval) == tuple:
            interval = range(*interval)

        return [i for i in (interval or range(len(self))) if self[i].has_node(node)]

    def pop(self, index: Optional[int] = None) -> StaticGraph:
        """
        Removes and returns graph snapshot at index.

        Raises an ``IndexError`` if graph is empty or index is out of range.

        :param index: Index of snapshot. Default: last snapshot.
        """
        self.__getitem__(index or -1)
        return self.data.pop(index or -1)


def _decorator_networkx(cls, method: str) -> Callable:
    """
    Decorator for static NetworkX graph methods.

    Returns a list of values returned by calling the method on each snapshot in the temporal graph.
    If all returned values are `None` or a boolean, returns a single element instead of a list.
    """
    def func(*args, **kwargs):
        returns = list(G.__getattribute__(method)(*args, **kwargs) for G in cls)
        if all(r is None for r in returns):
            return None
        if all(r is True for r in returns):
            return True
        if all(r is False for r in returns):
            return False
        return returns
    return func


def _wrapper_networkx(cls, G: StaticGraph) -> None:
    """
    Wrapper for decorating static NetworkX graph methods.
    """
    for method in dir(G):
        if method not in dir(TemporalBase) and not method.startswith("__"):
            try:
                cls.__setattr__(method, _decorator_networkx(cls, method))
            except AttributeError:  # networkx<2.8.1
                warn("NetworkX version <2.8.1 detected, inherited methods will be undocumented.")
