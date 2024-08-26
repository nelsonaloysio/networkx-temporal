from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional, Union

import networkx as nx

from .slice import slice
from ..methods.static import (
    is_directed,
    is_multigraph,
    neighbors,
    to_directed,
    to_undirected,
)
from ..methods.temporal import (
    temporal_degree,
    temporal_edges,
    temporal_in_degree,
    temporal_neighbors,
    temporal_nodes,
    temporal_order,
    temporal_out_degree,
    temporal_size,
    total_order,
    total_size,
)
from ..transform import (
    to_events,
    to_snapshots,
    to_static,
    to_unified,
)
from ..typing import TemporalGraph


class TemporalBase(metaclass=ABCMeta):
    """
    Base class for temporal graphs.

    This class is not meant to be instantiated directly, but rather inherited by the classes
    :class:`~networkx_temporal.TemporalGraph`, :class:`~networkx_temporal.TemporalDiGraph`,
    :class:`~networkx_temporal.TemporalMultiGraph`, and :class:`~networkx_temporal.TemporalMultiDiGraph`.
    """
    slice = slice

    # Static methods; override NetworkX methods.
    neighbors = neighbors
    is_directed = is_directed
    is_multigraph = is_multigraph
    to_directed = to_directed
    to_undirected = to_undirected

    # Temporal methods.
    temporal_degree = temporal_degree
    temporal_edges = temporal_edges
    temporal_in_degree = temporal_in_degree
    temporal_neighbors = temporal_neighbors
    temporal_nodes = temporal_nodes
    temporal_order = temporal_order
    temporal_out_degree = temporal_out_degree
    temporal_size = temporal_size
    total_order = total_order
    total_size = total_size

    # Transform methods.
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    @abstractmethod
    def __init__(self, t: Optional[int] = None, directed: bool = None, multigraph: bool = None):
        graph = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")
        self.data = [graph() for _ in range(t or 1)]

        list(
            self.__setattr__(method, wrap(self, method))
            for method in dir(graph)
            if method not in TemporalBase.__dict__
            and not method.startswith("_")
        )

    def __getitem__(self, t: Union[str, int, slice]) -> nx.Graph:
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

    def __repr__(self) -> str:
        """ Returns string representation of the class. """
        return f"Temporal"\
               f"{'Multi' if self.is_multigraph() else ''}"\
               f"{'Di' if self.is_directed() else ''}"\
               f"Graph (t={len(self)}) "\
               f"with {sum(self.order())} nodes and {sum(self.size())} edges"

    @property
    def data(self) -> list:
        """
        The ``data`` property of the temporal graph.

        :meta private:
        """
        return self.__dict__.get("_data", None)

    @data.setter
    def data(self, data: Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, list, dict]):
        """
        The ``data`` property of the temporal graph.

        :param data: NetworkX graph, list or dictionary of NetworkX graphs.

        :meta private:
        """
        assert type(data) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, list, dict),\
            f"Argument 'data' must be a NetworkX graph, list or dictionary, received: {type(data)}."

        names = list(data.keys()) if type(data) == dict else None
        data = data if type(data) == list else list(data.values()) if type(data) == dict else [data]

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
        The ``name`` property of the temporal graph.

        :param name: Name to give to temporal graph object.
            If ``None``, resets name to an empty string.
        """
        self.__dict__.pop("_name", None) if name is None else self.__setattr__("_name", name)

    @property
    def names(self) -> list:
        """
        The ``name`` property of each snapshot in the temporal graph.

        :getter: Returns names of temporal graph snapshots.
        :setter: Sets names of temporal graph snapshots.
        :rtype: list
        """
        return self.__dict__.get("_names", ["" for _ in range(len(self))])

    @names.setter
    def names(self, names: Optional[Union[list, tuple]]):
        """
        The ``name`` property of each snapshot in the temporal graph.

        :param names: Names to give to temporal graph snapshots.
            If ``None``, resets names to empty strings.
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

    def append(self, G: Optional[nx.Graph] = None) -> None:
        """
        Appends a new snapshot to the temporal graph.

        :param G: NetworkX graph to append. Optional.
        """
        self.insert(len(self), G)

    def flatten(self) -> TemporalGraph:
        """
        Returns flattened version of temporal graph.
        Same as :func:`~networkx_temporal.TemporalGraph.slice` with ``bins=1``.

        .. important::

            A flattened or static graph does not preserve dynamic node attributes.
        """
        return self.slice(bins=1)

    def insert(self, t: int, G: Optional[nx.Graph] = None) -> None:
        """
        Inserts a new snapshot to the temporal graph at a given index.

        :param t: Index of snapshot to insert.
        :param G: NetworkX graph to insert. Optional.
        """
        directed = self.is_directed()
        multigraph = self.is_multigraph()

        if G is None:
            G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()

        assert type(t) == int,\
            f"Argument `t` must be an integer, received: {type(t)}."

        assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
            f"Argument `G` must be a valid NetworkX graph, received: {type(G)}."

        assert G.is_directed() == directed,\
            f"Received a{' directed' if G.is_directed() else 'n undirected'} graph, "\
            f"but temporal graph is {'' if directed else 'un'}directed."

        assert G.is_multigraph() == multigraph,\
            f"Received a {'multi' if G.is_multigraph() else ''}graph, "\
            f"but temporal graph is {'' if multigraph else 'not '}a multigraph."

        self.data.insert(t, G)

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

    def pop(self, t: Optional[int] = None) -> nx.Graph:
        """
        Removes and returns the snapshot at a given time step.

        :param t: Index of snapshot to pop. Default: last snapshot.
        """
        self.__getitem__(t or -1)
        return self.data.pop(t or -1)


def wrap(self, method: str) -> Callable:
    """
    Decorator for wrapping static graph methods.

    Returns a list of values returned by calling the method on each snapshot in the temporal graph.
    If all returned values are `None` or a boolean, returns a single element instead of a list.

    :meta private:
    """
    def func(*args, **kwargs):
        returns = list(G.__getattribute__(method)(*args, **kwargs) for G in self)
        if all(r is None for r in returns):
            return None
        if all(r is True for r in returns):
            return True
        if all(r is False for r in returns):
            return False
        return returns
    return func
