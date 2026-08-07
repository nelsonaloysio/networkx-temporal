from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import Any, List, Optional, Union
from warnings import warn

import networkx as nx

from .functions import (
    edge_subgraph,
    neighbors as temporal_neighbors,
    from_multigraph,
    to_multigraph,
    subgraph,
)
from .slice import slice
from .wraps import (
    all_neighbors,
    copy,
    degree,
    in_degree,
    out_degree,
    neighbors,
    remove_edges_from,
    remove_nodes_from,
    to_directed,
    to_undirected,
    wrapper,
)
from ..algorithms.node.degree import (
    degree as temporal_degree,
    in_degree as temporal_in_degree,
    out_degree as temporal_out_degree,
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
    """ Abstract base class for temporal graphs.

    This class is not meant to be instantiated directly, but rather inherited by the classes
    :class:`~networkx_temporal.classes.TemporalGraph`,
    :class:`~networkx_temporal.classes.TemporalDiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiGraph`,
    and :class:`~networkx_temporal.classes.TemporalMultiDiGraph`.
    """
    convert = convert.convert
    copy = copy
    edge_subgraph = edge_subgraph
    from_multigraph = from_multigraph
    remove_edges_from = remove_edges_from
    remove_nodes_from = remove_nodes_from
    subgraph = subgraph
    to_directed = to_directed
    to_events = to_events
    to_multigraph = to_multigraph
    to_snapshots = to_snapshots
    to_static = to_static
    to_undirected = to_undirected
    to_unrolled = to_unrolled
    all_neighbors = all_neighbors
    neighbors = neighbors
    degree = degree
    in_degree = in_degree
    out_degree = out_degree
    slice = slice
    temporal_degree = temporal_degree
    temporal_in_degree = temporal_in_degree
    temporal_out_degree = temporal_out_degree

    @abstractmethod
    def __init__(self, t: int, create_using: StaticGraph):
        t = 0 if t is None else t  # Default to empty graph.

        if type(t) != int:
            raise TypeError(f"Argument `t` must be an integer, received: {type(t)}.")
        if t < 0:
            raise ValueError(f"Argument `t` must be a non-negative integer, received: {t}.")
        if type(create_using) == type:
            create_using = create_using()

        self._directed = create_using.is_directed()
        self._multigraph = create_using.is_multigraph()

        # Initialize empty snapshots.
        self.graphs = [create_using.__class__() for _ in range(t)]

        # Inherit methods from NetworkX graph.
        for name in dir(create_using):
            if not name.startswith("__") and name not in dir(TemporalABC):
                try:
                    setattr(self, name, wrapper(self, create_using, name))
                except AttributeError:  # networkx<2.8.1
                    warn("NetworkX version <2.8.1: inherited methods will be undocumented.")

    def __getitem__(self, t: Any) -> StaticGraph:
        """ Returns snapshot from a given interval. """
        if len(self.graphs) == 0:
            raise IndexError("Temporal graph is empty (t=0), cannot index snapshots.")
        if type(t) == int and (t >= len(self) or t < -len(self)):
            raise IndexError(f"Received index {t}, but temporal graph has {len(self)} snapshots.")
        if type(t) == str and not self.index:
            raise IndexError("Temporal graph `index` property is unset; cannot index by string.")

        if type(t) == int:
            return self.graphs[t]
        if type(t) == str:
            return self.graphs[self.index.index(t)]

        TG = self.__class__(t=0)
        TG.graphs = {t: G for t, G in self.items()}
        return TG

    def __iter__(self) -> iter:
        """ Returns iterator over slices in the temporal graph. """
        if len(self.graphs) == 0:
            self.add_snapshot()  # Ensure at least one snapshot for iteration.
            # raise IndexError("Temporal graph is empty (t=0), cannot iterate snapshots.")
        return iter(self.graphs)

    def __len__(self) -> int:
        """ Returns number of slices in the temporal graph. """
        return len(self.graphs)

    def __setitem__(self, t: Any, G: StaticGraph) -> None:
        """ Sets snapshot for a given interval. """
        if type(t) == int:
            self.graphs[t] = G
        elif type(t) == str:
            self.graphs[self.index.index(t)] = G

    def __str__(self) -> str:
        """ Returns string representation of the class. """
        return f"Temporal"\
               f"{'Multi' if self.is_multigraph() else ''}"\
               f"{'Di' if self.is_directed() else ''}"\
               f"Graph "\
               f"""{f"named '{self.name}' " if self.name else ''}"""\
               f"(t={len(self)}) "\
               f"with {self.order(copies=False)} nodes and {self.size(copies=True)} edges"

    # -- Properties -- #

    @property
    def t(self) -> int:
        """ The ``t`` property of the temporal graph.

        Returns number of snapshots. Implemented for cohesiveness with ``__str__`` representation.

        :getter: Returns number of snapshots.
        :rtype: int

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.__len__`.
        """
        return len(self)

    @property
    def graph(self) -> dict:
        """ The ``graph`` property of the temporal graph. Preserved on :func:`~networkx_temporal.classes.TemporalGraph.to_static` conversion.
        """
        self._graph = self.__dict__.get("_graph") or {}
        return self._graph

    @property
    def graphs(self) -> list:
        """ The ``graphs`` property of the temporal graph.

        :getter: Returns temporal graph data.
        :setter: Sets temporal graph data. Accepts a list, tuple, or dictionary of NetworkX graphs.
            Passing a dictionary will set the ``index`` property to its keys.
        :rtype: list
        """
        return self.__dict__.get("_graphs", None)

    @graphs.setter
    def graphs(self, graphs: Union[StaticGraph, list, dict, tuple]):
        """ Setter for the ``graphs`` property of the temporal graph.
        """
        if type(graphs) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
            graphs = [graphs]

        index = list(graphs.keys()) if type(graphs) == dict else None
        graphs = list(graphs.values() if type(graphs) == dict else graphs)

        if not all(
            type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)
            for G in graphs
        ):
            raise TypeError(
                f"Argument `graphs` expects static NetworkX graph objects as input."
            )
        if any(G.is_directed() != self.is_directed() for G in graphs):
            raise ValueError(
                f"Received a{' directed' if G.is_directed() else 'n undirected'} graph, "
                f"but temporal graph is {'' if self.is_directed() else 'un'}directed."
            )
        if any(G.is_multigraph() != self.is_multigraph() for G in graphs):
            raise ValueError(
                f"Received a {'multi' if G.is_multigraph() else ''}graph, "
                f"but temporal graph is {'' if self.is_multigraph() else 'not '}a multigraph."
            )

        self._graphs = graphs
        self._index = index

    @property
    def index(self) -> list:
        """ The ``index`` property of the temporal graph. Used to store intervals as strings on
        :func:`~networkx_temporal.classes.TemporalGraph.slice`.

        :getter: Returns index of temporal graph snapshots.
        :setter: Sets index of temporal graph snapshots.
        :rtype: list
        """
        return self.__dict__.get("_index", range(len(self)))

    @index.setter
    def index(self, index: List[str]) -> None:
        """ Setter for the ``index`` property of the temporal graph.
        """
        if index is None:
            self.__dict__.pop("_index", None)
            return
        if len(index) != len(self):
            raise ValueError(
                f"Length of index ({len(index)}) differs from number of snapshots ({len(self)})."
            )
        if not any(all(type(i) == dtype for i in index) for dtype in (str, int)):
            raise TypeError("All elements in index must be strings or integers.")
        if type(index[0]) == str and len(index) != len(set(index)):
            raise ValueError("All elements in index must be unique.")

        # NOTE: Does not work if graphs are views, as setting one view will set all objects.
        # list(setattr(self[t], "name", index[t]) for t in range(len(self)))
        self._index = index

    @property
    def name(self) -> str:
        """ The ``name`` property of the temporal graph.

        :getter: Returns temporal graph name.
        :setter: Sets temporal graph name.
        :rtype: str
        """
        return self.graph.get("name", None)

    @name.setter
    def name(self, name: Any):
        """ Setter for the ``name`` property of the temporal graph.
        """
        if name is None:
            self.graph.pop("name", None)
            return
        if type(name) != str:
            raise TypeError(f"Argument `name` must be a string, received: {type(name)}.")
        self.graph["name"] = name

    @property
    def names(self) -> list:
        """ The ``names`` property of the temporal graph.\n:meta private:
        """
        warn("TemporalGraph `names` property is deprecated in favor of `index` and will be removed"
             "in a future release.", DeprecationWarning)
        return self.index

    @names.setter
    def names(self, names: Optional[List[str]]):
        """ Setter for the ``names`` property of the temporal graph.\n:meta private:
        """
        warn("TemporalGraph `names` setter is deprecated in favor of `index` and will be removed"
             "in a future release.", DeprecationWarning)
        self.index = names

    # -- Graph-specific methods -- #

    def edge(self, *edge) -> Optional[List[str]]:
        """ Returns a dictionary mapping each edge to their temporal attributes,
        with snapshot indices as keys and dictionaries as values.

        :param edge: Edge to get data for.
        """
        return {t: G.edges[edge] for t, G in self.items() if G.has_edge(*edge)}

    def node(self, node) -> Optional[List[str]]:
        """ Returns a dictionary mapping each node to their temporal attributes,
        with snapshot indices as keys and dictionaries as values.

        :param node: Node to get data for.
        """
        return {t: G.nodes[node] for t, G in self.items() if G.has_node(node)}

    def edges(self, *args, copies: Optional[bool] = None, **kwargs) -> Optional[List[str]]:
        """ Returns a mapping of edges and temporal data.

        :param copies: If set, returns a single list of edges across all snapshots,
            with duplicates if ``True``, and without duplicates if ``False``.
        """
        if len(self) == 0:
            return []
        if copies is None:
            return [G.edges(*args, **kwargs) for G in self]
        return self.temporal_edges(copies=copies, *args, **kwargs)

    def nodes(self, *args, copies: Optional[bool] = None, **kwargs) -> dict:
        """ Returns a mapping of nodes and temporal data.

        :param copies: If set, returns a single list of nodes across all snapshots,
            with duplicates if ``True``, and without duplicates if ``False``.
        """
        if len(self) == 0:
            return []
        if copies is None:
            return [G.nodes(*args, **kwargs) for G in self]
        return self.temporal_nodes(copies=copies, *args, **kwargs)

    def add_snapshot(self, G: StaticGraph = None) -> StaticGraph:
        """ Adds a snapshot to the temporal graph.

        If ``G`` is ``None``, adds an empty graph with the same properties as the temporal graph.
        Returns the added snapshot (i.e., the parameter ``G`` if not ``None``, or an empty graph).

        :param G: NetworkX graph object to add as snapshot.
        """
        if G is None:
            G = self.new_snapshot()
        self.insert(len(self), G)
        return G

    def add_snapshots_from(self, graphs: List[StaticGraph]) -> None:
        """ Adds multiple snapshots to the temporal graph.

        :param graphs: List of NetworkX graph objects to add as snapshots.
        """
        for G in graphs:
            self.insert(len(self), G)

    def flatten(self) -> TemporalGraph:
        """ Returns ''flattened'' version of temporal graph.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.slice` with ``bins=1``.

        This method differs from :func:`~networkx_temporal.classes.TemporalGraph.to_static` only in
        the sense that it returns a :class:`~networkx_temporal.classes.TemporalGraph` object with a
        single snapshot, rather than a static NetworkX graph object (i.e., the snapshot).

        .. attention::

           As each node in a flattened graph is unique, dynamic node attributes are not preserved.
           Parallel edges from different snapshots are also not preserved, except for multigraphs.
        """
        return self.slice(bins=1)

    def get_edge_data(self, *edge) -> Optional[List[str]]:
        """ Returns a dictionary mapping each edge to their temporal attributes,
        with snapshot indices as keys and dictionaries as values.

        :param edge: Edge to get data for.
        """
        return [G.get_edge_data(*edge) for G in self if G.has_edge(*edge)]

    def get_node_data(self, node: Any) -> list:
        """ Returns a list of all attributes for a given node across all snapshots.

        :param node: Node to get data for.
        """
        return [G._node[node] if G.has_node(node) else None for G in self]

    def index_edge(self, edge: tuple, interval: Optional[range] = None) -> list:
        """ Returns index of all snapshots in which an edge is present.

        :param edge: Edge to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
        """
        if interval is not None and type(interval) not in (range, tuple, list):
            raise TypeError("Argument `interval` must be a range of integers.")

        if interval is None:
            interval = range(len(self))
        else:
            interval = range(*interval) or range(interval[0], interval[1]+1)

        return [i for i in (interval or range(len(self))) if self[i].has_edge(*edge)]

    def index_node(self, node: Any, interval: Optional[range] = None) -> list:
        """ Returns index of all snapshots in which a node is present.

        :param node: Node to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
        """
        if interval is not None and type(interval) not in (range, tuple, list):
            raise TypeError("Argument `interval` must be a range of integers.")

        if interval is None:
            interval = range(len(self))
        elif type(interval) in (tuple, list):
            interval = range(*interval) or range(interval[0], interval[1]+1)

        return [i for i in (interval or range(len(self))) if self[i].has_node(node)]

    def index_snapshot(self, snapshot: StaticGraph, interval: Optional[range] = None) -> list:
        """ Returns index of all occurrences of a given snapshot.

        :param snapshot: Snapshot (NetworkX graph) to look for.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
        """
        if type(snapshot) not in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
            raise TypeError("Argument `snapshot` must be a valid NetworkX graph object.")
        return [i for i in (interval or range(len(self))) if self[i] == snapshot]

    def is_directed(self) -> bool:
        """ Returns ``True`` if the temporal graph is directed.
        """
        return bool(self.__dict__.get("_directed", None))

    def is_multigraph(self) -> bool:
        """ Returns ``True`` if the temporal graph is a multigraph.
        """
        return bool(self.__dict__.get("_multigraph", None))

    def new_snapshot(self) -> StaticGraph:
        """ Returns a new empty snapshot of the same type as the temporal graph.
        """
        fnc = f"{'Multi' if self.is_multigraph() else ''}{'Di' if self.is_directed() else ''}Graph"
        return getattr(nx, fnc)()

    def number_of_edges(self, weight: Optional[bool] = None, copies: Optional[bool] = None) -> int:
        """ Returns number of edges in the temporal graph.

        :param weight: The edge attribute that holds the numerical value used as a weight.
            If ``None`` (default), then each edge has weight 1.
        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. If ``False``, consider unique edges. Optional.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.size`.
        """
        return self.size(weight=weight, copies=copies)

    def number_of_neighbors(self, node: Any) -> list:
        """ Returns number of neighbors for each snapshot.

        :param node: Node to get number of neighbors for.
        """
        return [len(list(G.neighbors(node))) if G.has_node(node) else 0 for G in self]

    def number_of_nodes(self, copies: Optional[bool] = None) -> int:
        """ Returns number of nodes in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. If ``False``, consider unique nodes. Optional.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.order`.
        """
        return self.order(copies=copies)

    def number_of_snapshots(self) -> int:
        """ Returns number of elements stored in
        :func:`~networkx_temporal.classes.TemporalGraph.graphs`.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.__len__`.
        """
        return len(self)

    def offsets(self, node: Optional[Any] = None) -> list:
        """ Returns list of node offsets for each snapshot in the temporal graph.

        :param node: Node to get offsets for. Returns ``None`` for snapshots it is not present in.
        """
        if node is not None:
            return [
                list(self[t].nodes).index(node) + sum(self[i].order() for i in range(t))
                if self[t].has_node(node) else None for t in range(len(self))
            ]
        return [sum(self[i].order() for i in range(t)) for t in range(len(self))]

    def order(self, copies: Optional[bool] = None) -> int:
        """ Returns number of nodes in the temporal graph.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. If ``False``, consider unique nodes. Optional.
        """
        if len(self) == 0:
            return 0
        if copies is None:
            return [G.order() for G in self]
        if copies is True:
            return sum(G.order() for G in self)
        if copies is False:
            return len(set(self.temporal_nodes()))
        raise TypeError(f"Argument `copies` must be of type bool, received: {type(copies)}.")

    def remove_snapshot(self, G: StaticGraph) -> None:
        """ Removes first occurrence of snapshot ``G`` (a NetworkX graph) from the temporal graph.

        :param G: NetworkX graph object to remove.
        """
        if type(G) not in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
            raise TypeError(f"Argument `G` must be a valid NetworkX graph, received: {type(G)}.")
        self.graphs.remove(G)

    def size(self, weight: Optional[bool] = None, copies: Optional[bool] = None) -> int:
        """ Returns number of edges in the temporal graph.

        :param weight: The edge attribute that holds the numerical value used as a weight.
            If ``None`` (default), then each edge has weight 1.
        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. If ``False``, consider unique edges. Optional.
        """
        if len(self) == 0:
            return 0
        if copies is None:
            return [G.size(weight=weight) for G in self]
        if copies is True:
            return sum(G.size(weight=weight) for G in self)
        if copies is False:
            if weight is not None and weight is not False:
                raise ValueError("Argument `weight` is not compatible with `copies=False`.")
            return len(set(self.temporal_edges()))
        raise TypeError(f"Argument `copies` must be of type bool, received: {type(copies)}.")

    def snapshots(self) -> list:
        """ Returns list of snapshots in the temporal graph.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.graphs`.
        """
        return self.graphs

    def temporal_edges(self, copies: Optional[bool] = None, *args, **kwargs) -> Union[list, dict]:
        """ Returns sequence of edges (interactions) in all snapshots.

        :param copies: If ``True``, consider multiple instances of the same edge in different
            snapshots. Default is ``True``.
        :param args: Additional arguments to pass to the NetworkX graph method.
        :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
        """
        copies = True if copies is None else copies
        if len(self) == 0:
            return []
        if copies is False:
            if kwargs.get("data", None):
                return {k: v for G in self for k, v in G.edges(*args, **kwargs)}
            return {e for G in self for e in G.edges(*args, **kwargs)}
        return list(e for G in self for e in G.edges(*args, **kwargs))

    def temporal_nodes(self, copies: Optional[bool] = None, *args, **kwargs) -> Union[list, dict]:
        """ Returns sequence of nodes in all snapshots.

        :param copies: If ``True``, consider multiple instances of the same node in different
            snapshots. Default is ``False``.
        :param args: Additional arguments to pass to the NetworkX graph method.
        :param kwargs: Additional keyword arguments to pass to the NetworkX graph method.
        """
        copies = False if copies is None else copies
        if len(self) == 0:
            return []
        if copies is False:
            if kwargs.get("data", None):
                return {k: v for G in self for k, v in G.nodes(*args, **kwargs)}
            return {n for G in self for n in G.nodes(*args, **kwargs)}
        return list(n for G in self for n in G.nodes(*args, **kwargs))

    def temporal_neighbors(self, node: Any) -> list:
        """ Returns single list of neighbors for a given node across all snapshots.

        :param node: Node to get neighbors for.
        """
        return list(temporal_neighbors(self, node))

    def temporal_order(self) -> int:
        """ Return number of unique nodes.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.total_order` method for the sum of
            of nodes in all snapshots.
        """
        return self.order(copies=False)

    def temporal_size(self) -> int:
        """ Return number of unique interactions.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=False``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.total_size` method for the sum of
            edges in all snapshots.
        """
        return self.size(copies=False)

    def timestamps(self, attr: Optional[str] = None, default: Any = None) -> list:
        """ Returns list of snapshot indices for each edge in the temporal graph.

        :param attr: Edge attribute to use as timestamp. By default, consider current slicing
            of the temporal graph as timestamps (i.e., snapshot indices). Optional.
        :param default: Value to use for missing timestamps if ``attr`` is not ``None``.
        """
        if attr:
            return [d for G in self for _, _, d in G.edges(data=attr, default=default)]
        return [t for t, m in enumerate(self.size()) for _ in range(m)]

    def total_order(self) -> int:
        """ Return sum of nodes from all snapshots.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.order` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.temporal_order` method for the
            number of unique nodes in the temporal graph.
        """
        return self.order(copies=True)

    def total_size(self, weight: Optional[str] = "weight") -> int:
        """ Return sum of edges from all snapshots.
        Equivalent to :func:`~networkx_temporal.classes.TemporalGraph.size` with ``copies=True``.

        .. seealso::

            The :func:`~networkx_temporal.classes.TemporalGraph.temporal_size` method for the
            number of unique interactions in the temporal graph.

        :param weight: The edge attribute that holds the numerical value used as a weight.
            If ``None`` (default), then each edge has weight 1.
        """
        return self.size(weight=weight, copies=True)

    # -- List-like methods -- #

    def append(self, G: Optional[StaticGraph] = None) -> None:
        """ Adds a new snapshot ``G`` to the temporal graph.
        If unset, adds an empty graph.

        :param G: NetworkX graph object to append. Optional.
        """
        self.insert(len(self), G)

    def insert(self, index: int, G: Optional[StaticGraph] = None) -> None:
        """ Inserts a new snapshot to the temporal graph at a given index.

        :param index: Insert graph object before index.
        :param G: NetworkX graph object to insert. Optional.
        """
        directed = self.is_directed()
        multigraph = self.is_multigraph()

        if G is None:
            G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()

        if type(index) != int:
            raise TypeError(
                f"Index must be an integer, received: {type(index)}."
            )
        if not (type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
            raise TypeError(
                (f"Input must be a static NetworkX graph, received: {type(G)}.")
            )
        if G.is_directed() != directed:
            raise ValueError(
                f"Received a{' directed' if G.is_directed() else 'n undirected'} graph, "
                f"but temporal graph is {'' if directed else 'un'}directed."
            )
        if G.is_multigraph() != multigraph:
            raise ValueError(
                f"Received a {'multi' if G.is_multigraph() else ''}graph, "
                f"but temporal graph is {'' if multigraph else 'not '}a multigraph."
            )
        self.graphs.insert(index, G)

    # -- Dictionary-like methods -- #

    def items(self) -> tuple:
        """ Returns list of snapshot name and graph pairs.

        :note: Returns pairs of :func:`~networkx_temporal.classes.TemporalGraph.index` and
            :func:`~networkx_temporal.classes.TemporalGraph.graphs`.
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple:
        """ Returns a tuple of snapshot index.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.index`.
        """
        return tuple(self.index) if self.index is not None else tuple(range(len(self)))

    def pop(self, index: Optional[int] = -1) -> StaticGraph:
        """ Removes and returns graph snapshot at ``index`` (default: last snapshot).

        :param index: Index of snapshot. Default: last snapshot.
        """
        self.__getitem__(index)
        return self.graphs.pop(index)

    def values(self) -> tuple:
        """ Returns a tuple of snapshot graphs.

        :note: Alias to :func:`~networkx_temporal.classes.TemporalGraph.graphs`.
        """
        return tuple(self.graphs)

    # -- Wrappers for temporal methods -- #

    @wraps(degree)
    def total_degree(self, *args, **kwargs) -> list:
        return self.temporal_degree(*args, **kwargs)
    total_degree.__doc__ += "\n:meta private:"

    @wraps(in_degree)
    def total_in_degree(self, *args, **kwargs) -> list:
        return self.temporal_in_degree(*args, **kwargs)
    total_in_degree.__doc__ += "\n:meta private:"

    @wraps(out_degree)
    def total_out_degree(self, *args, **kwargs) -> list:
        return self.temporal_out_degree(*args, **kwargs)
    total_out_degree.__doc__ += "\n:meta private:"
