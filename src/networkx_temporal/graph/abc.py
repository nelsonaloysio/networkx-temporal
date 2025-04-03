from abc import ABCMeta, abstractmethod
from functools import reduce, wraps
from typing import Any, Optional, Union
from warnings import warn

import networkx as nx

from .order import order
from .size import size
from .slice import slice
from .wrapper import wrapper
from ..algorithms import (
    degree,
    in_degree,
    out_degree,
)
from ..transform import (
    to_events,
    to_snapshots,
    to_static,
    to_unified
)
from ..typing import StaticGraph, TemporalGraph
from ..utils import convert


class TemporalABC(metaclass=ABCMeta):
    """
    Abstract base class for temporal graphs.

    This class is not meant to be instantiated directly, but rather inherited by the classes
    :class:`~networkx_temporal.graph.TemporalGraph`,
    :class:`~networkx_temporal.graph.TemporalDiGraph`,
    :class:`~networkx_temporal.graph.TemporalMultiGraph`,
    and :class:`~networkx_temporal.graph.TemporalMultiDiGraph`.
    """
    convert = convert.convert
    slice = slice
    order = order
    size = size
    total_degree = degree
    total_in_degree = in_degree
    total_out_degree = out_degree
    # transform
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    @abstractmethod
    def __init__(self, t: int, create_using: StaticGraph):
        self.data = [nx.empty_graph(create_using=create_using) for _ in range(t or 1)]

        # NOTE: MultiDiGraph is a subclass of MultiGraph; fixed by using dir() and not __dict__.
        # create_using = (nx.MultiGraph if create_using == nx.MultiDiGraph else create_using)

        # Inherit methods from NetworkX graph.
        for name in dir(create_using):
            if not name.startswith("__") and name not in dir(TemporalABC):
                try:
                    setattr(self, name, wrapper(self, name))
                except AttributeError:  # networkx<2.8.1
                    warn("NetworkX version <2.8.1: inherited methods will be undocumented.")

    def __getitem__(self, t: Union[str, int, range]) -> StaticGraph:
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
               f"with {self.order(copies=False)} nodes and {self.size(copies=True)} edges"

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

        This method differs from :func:`~networkx_temporal.graph.TemporalGraph.to_static` only in
        the sense that it returns a :class:`~networkx_temporal.graph.TemporalGraph` object with a
        single snapshot, rather than a static NetworkX graph object.

        .. attention::

           As each node in a flattened graph is unique, dynamic node attributes are not preserved.
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
        Removes and returns graph snapshot at index.

        Raises an ``IndexError`` if graph is empty or index is out of range.

        :param index: Index of snapshot. Default: last snapshot.
        """
        self.__getitem__(index or -1)
        return self.data.pop(index or -1)

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

    @wraps(degree)
    def temporal_degree(self, *args, **kwargs) -> list:
        warn("`temporal_degree` deprecated in favor of `total_degree`.", DeprecationWarning)
        return self.total_degree(*args, **kwargs)

    @wraps(in_degree)
    def temporal_in_degree(self, *args, **kwargs) -> list:
        warn("`temporal_in_degree` deprecated in favor of `total_in_degree`.", DeprecationWarning)
        return self.total_in_degree(*args, **kwargs)

    @wraps(out_degree)
    def temporal_out_degree(self, *args, **kwargs) -> list:
        warn("`temporal_out_degree` deprecated in favor of `total_out_degree`.", DeprecationWarning)
        return self.total_out_degree(*args, **kwargs)

    def temporal_order(self) -> int:
        """
        Return number of unique nodes in all snapshots.
        Equivalent to :func:`~networkx_temporal.graph.TemporalGraph.order` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.graph.TemporalGraph.total_order` method for the sum of
            the number of nodes in all snapshots.
        """
        return self.order(copies=False)

    def temporal_size(self) -> int:
        """
        Return number of unique edges in all snapshots.
        Equivalent to :func:`~networkx_temporal.graph.TemporalGraph.size` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.graph.TemporalGraph.total_order` method for the sum of
            the number of edges in all snapshots.
        """
        return self.size(copies=False)

    def total_order(self) -> int:
        """
        Return sum of nodes from all snapshots.
        Equivalent to :func:`~networkx_temporal.graph.TemporalGraph.order` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.graph.TemporalGraph.temporal_order` method for the
            number of unique nodes in the temporal graph.
        """
        return self.order(copies=True)

    def total_size(self) -> int:
        """
        Return sum of edges from all snapshots.
        Equivalent to :func:`~networkx_temporal.graph.TemporalGraph.size` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.graph.TemporalGraph.temporal_size` method for the
            number of unique edges in the temporal graph.
        """
        return self.size(copies=True)

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
        return self.__static_degree("degree", nbunch=nbunch, weight=weight)

    # NOTE: docstring of nx.DiGraph.in_degree: ERROR: Unexpected indentation.
    # @wraps(nx.DiGraph.in_degree)
    @wraps(nx.Graph.degree)
    def in_degree(self, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
        return self.__static_degree("in_degree", nbunch=nbunch, weight=weight)

    @wraps(nx.Graph.neighbors)
    def neighbors(self, node: Any) -> iter:
        yield from list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)

    # NOTE: docstring of nx.DiGraph.out_degree: ERROR: Unexpected indentation.
    # @wraps(nx.DiGraph.out_degree)
    @wraps(nx.Graph.degree)
    def out_degree(self, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
        return self.__static_degree("out_degree", nbunch=nbunch, weight=weight)

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

    def __static_degree(self, degree: str, nbunch: Any = None, weight: str = None) -> Union[dict, int]:
        degrees = [getattr(G, degree)(nbunch=nbunch, weight=weight) for G in self]

        if nbunch is None or isinstance(nbunch, (list, tuple)):
            return [dict(d) for d in degrees]

        return [d if type(d) == int else None for d in degrees]

    copy.__doc__ += "\n:meta private:"
    degree.__doc__ += "\n:meta private:"
    in_degree.__doc__ += "\n:meta private:"
    neighbors.__doc__ += "\n:meta private:"
    out_degree.__doc__ += "\n:meta private:"
    to_directed.__doc__ += "\n:meta private:"
    to_undirected.__doc__ += "\n:meta private:"
    temporal_degree.__doc__ += "\n:meta private:"
    temporal_in_degree.__doc__ += "\n:meta private:"
    temporal_out_degree.__doc__ += "\n:meta private:"