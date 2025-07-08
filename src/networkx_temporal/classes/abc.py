from abc import ABCMeta, abstractmethod
from functools import reduce, wraps
from typing import Any, Optional, Union
from warnings import warn

import networkx as nx
from networkx.exception import NetworkXError

from .networkx import (
    # all_neighbors,
    copy,
    degree,
    in_degree,
    out_degree,
    neighbors,
    to_directed,
    to_undirected,
    wrapper,
)
from .slice import _slice
from ..algorithms import (
    degree as total_degree,
    in_degree as total_in_degree,
    out_degree as total_out_degree,
)
from ..transform import (
    to_events,
    to_snapshots,
    to_static,
    to_unrolled
)
from ..typing import StaticGraph, TemporalGraph
from ..utils import convert


class TemporalABC(metaclass=ABCMeta):
    """
    Abstract base class for temporal graphs.

    This class is not meant to be instantiated directly, but rather inherited by the classes
    :class:`~networkx_temporal.classes.TemporalGraph`,
    :class:`~networkx_temporal.classes.TemporalDiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiGraph`,
    and :class:`~networkx_temporal.classes.TemporalMultiDiGraph`.
    """
    convert = convert.convert
    all_neighbors = copy
    copy = copy
    degree = degree
    in_degree = in_degree
    neighbors = neighbors
    out_degree = out_degree
    to_directed = to_directed
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_undirected = to_undirected
    to_unrolled = to_unrolled
    total_degree = total_degree
    total_in_degree = total_in_degree
    total_out_degree = total_out_degree

    @abstractmethod
    def __init__(self, t: int, create_using: StaticGraph):
        assert t is None or type(t) == int,\
            f"Argument `t` must be an integer, received: {type(t)}."
        assert t is None or t > 0,\
            f"Argument `t` must be a positive integer, received: {t}."

        self.data = [nx.empty_graph(create_using=create_using) for _ in range(t or 1)]

        # Inherit methods from NetworkX graph.
        for name in dir(create_using):
            if not name.startswith("__") and name not in dir(TemporalABC):
                try:
                    setattr(self, name, wrapper(self, name))
                except AttributeError:  # networkx<2.8.1
                    warn("NetworkX version <2.8.1: inherited methods will be undocumented.")

    def __getitem__(self, t: Union[str, int, range]) -> StaticGraph:
        """ Returns snapshot from a given interval. """
        # assert self.data,\
        #     "Temporal graph is empty."
        # assert type(t) != str or self.names,\
        #     "Temporal graph snapshots are not named."
        # assert type(t) != int or -len(self) <= t < len(self),\
        #     f"Received index {t}, but temporal graph has {len(self)} snapshots."
        # assert type(t) != slice or -len(self) <= (t.start or 0) < (t.stop or len(self)) <= len(self),\
        #     f"Received slice {t.start, t.stop}, but temporal graph has {len(self)} snapshots."

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
               f"with {self.order(copies=False)} nodes and {self.size(copies=True)} edges"

    @wraps(_slice)
    def slice(self, *args, **kwargs) -> TemporalGraph:
        """ Returns a sliced temporal graph. """
        return _slice(self, *args, **kwargs)

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

        names = list(data.keys()) if type(data) == dict else None
        data = list(data.values() if type(data) == dict else data)

        assert all(type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for G in data),\
            f"Argument 'data' must be a list, tuple, or dictionary of NetworkX graphs, "\
            f"received: {type(data)}."

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
        :func:`~networkx_temporal.classes.TemporalGraph.slice`.

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
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.slice` with ``bins=1``.

        This method differs from :func:`~networkx_temporal.classes.TemporalGraph.to_static` only in
        the sense that it returns a :class:`~networkx_temporal.classes.TemporalGraph` object with a
        single snapshot, rather than a static NetworkX graph object (i.e., the snapshot).

        .. attention::

           As each node in a flattened graph is unique, dynamic node attributes are not preserved.
           Parallel edges from different snapshots are also not preserved, except for multigraphs.
        """
        return self.slice(bins=1)

    def index_edge(self, edge: tuple, interval: Optional[range] = None) -> list:
        """
        Returns index of all snapshots in which an edge is present.

        :param edge: Edge to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
        """
        assert interval is None or type(interval) in (range, tuple, list),\
            "Argument `interval` must be a range of integers."

        if interval is None:
            interval = range(len(self))
        elif type(interval) in (tuple, list):
            interval = range(*interval) or range(interval[0], interval[1]+1)

        return [i for i in (interval or range(len(self))) if self[i].has_edge(*edge)]

    def index_node(self, node: Any, interval: Optional[range] = None) -> list:
        """
        Returns index of all snapshots in which a node is present.

        :param node: Node to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
        """
        assert interval is None or type(interval) in (range, tuple, list),\
            "Argument `interval` must be a range of integers."

        if interval is None:
            interval = range(len(self))
        elif type(interval) in (tuple, list):
            interval = range(*interval) or range(interval[0], interval[1]+1)

        return [i for i in (interval or range(len(self))) if self[i].has_node(node)]

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

    def pop(self, index: Optional[int] = None) -> StaticGraph:
        """
        Removes and returns graph snapshot at ``index`` (default: last snapshot).

        :param index: Index of snapshot. Default: last snapshot.
        """
        self.__getitem__(index or -1)
        return self.data.pop(index or -1)

    def all_neighbors(self, node: Any) -> iter:
        """
        Returns iterator of node neighbors for each snapshot. Does not consider edge direction.

        :param node: Node to get neighbors for.
        """
        yield from list(list(nx.all_neighbors(G, node)) if G.has_node(node) else [] for G in self)

    def neighbors(self, node: Any) -> iter:
        """
        Returns iterator of node neighbors for each snapshot. Considers edge direction.

        :param node: Node to get neighbors for.
        """
        yield from list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)

    def number_of_edges(self, copies: Optional[bool] = None) -> int:
        """
        Returns number of edges in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. If ``False``, consider unique edges. Optional.

        :note: Alias for :func:`~networkx_temporal.classes.TemporalGraph.size`.
        """
        return self.size(copies=copies)

    def number_of_neighbors(self, node: Any) -> list:
        """
        Returns number of neighbors for each snapshot.

        :param node: Node to get number of neighbors for.
        """
        return [len(list(G.neighbors(node))) if G.has_node(node) else 0 for G in self]

    def number_of_nodes(self, copies: Optional[bool] = None) -> int:
        """
        Returns number of nodes in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. If ``False``, consider unique nodes. Optional.

        :note: Alias for :func:`~networkx_temporal.classes.TemporalGraph.order`.
        """
        return self.order(copies=copies)

    def order(self, copies: Optional[bool] = None) -> int:
        """
        Returns number of nodes in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. If ``False``, consider unique nodes. Optional.
        """
        if copies is None:
            return [G.order() for G in self]
        if copies is True:
            return sum(G.order() for G in self)
        if copies is False:
            return len(set(self.temporal_nodes()))
        raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")

    def size(self, copies: Optional[bool] = None) -> int:
        """
        Returns number of edges in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. If ``False``, consider unique edges. Optional.
        """
        if copies is None:
            return [G.size() for G in self]
        if copies is True:
            return sum(G.size() for G in self)
        if copies is False:
            return len(set(self.temporal_edges()))
        raise TypeError(f"Argument 'copies' must be of type bool, received: {type(copies)}.")

    def temporal_edges(self, copies: Optional[bool] = None, *args, **kwargs) -> list:
        """
        Returns list of edges (interactions) in all snapshots.

        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. Default is ``True``.
        :param args: Additional arguments to pass to the NetworkX graph method.
        :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
        """
        if copies is False:
            return reduce(lambda x, y: x.union(y), [set(G.edges(*args, **kwargs)) for G in self])
        return list(e for G in self for e in G.edges(*args, **kwargs))

    def temporal_nodes(self, copies: Optional[bool] = None, *args, **kwargs) -> list:
        """
        Returns list of nodes in all snapshots.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. Default is ``False``.
        :param args: Additional arguments to pass to the NetworkX graph method.
        :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
        """
        copies = False if copies is None else copies
        if copies is False:
            return reduce(lambda x, y: x.union(y), [set(G.nodes(*args, **kwargs)) for G in self])
        return list(e for G in self for e in G.nodes(*args, **kwargs))

    def temporal_order(self) -> int:
        """
        Return number of unique nodes.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.total_order` method for the sum of
            the number of nodes in all snapshots.
        """
        return self.order(copies=False)

    def temporal_size(self) -> int:
        """
        Return number of unique edges.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.total_order` method for the sum of
            the number of edges in all snapshots.
        """
        return self.size(copies=False)

    def total_order(self) -> int:
        """
        Return sum of nodes from all snapshots.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.temporal_order` method for the
            number of unique nodes in the temporal graph.
        """
        return self.order(copies=True)

    def total_size(self) -> int:
        """
        Return sum of edges from all snapshots.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.temporal_size` method for the
            number of unique edges in the temporal graph.
        """
        return self.size(copies=True)

    @wraps(total_degree)
    def temporal_degree(self, *args, **kwargs) -> list:
        warn("`temporal_degree` deprecated in favor of `total_degree`.", DeprecationWarning)
        return self.total_degree(*args, **kwargs)
    temporal_degree.__doc__ += "\n:meta private:"

    @wraps(total_in_degree)
    def temporal_in_degree(self, *args, **kwargs) -> list:
        warn("`temporal_in_degree` deprecated in favor of `total_in_degree`.", DeprecationWarning)
        return self.total_in_degree(*args, **kwargs)
    temporal_in_degree.__doc__ += "\n:meta private:"

    @wraps(total_out_degree)
    def temporal_out_degree(self, *args, **kwargs) -> list:
        warn("`temporal_out_degree` deprecated in favor of `total_out_degree`.", DeprecationWarning)
        return self.total_out_degree(*args, **kwargs)
    temporal_out_degree.__doc__ += "\n:meta private:"
