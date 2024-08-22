from __future__ import annotations

from typing import Any, Callable, Optional, Union

import networkx as nx

from .slice import slice
from ..metrics.static import neighbors
from ..metrics.temporal import (
    temporal_degree,
    temporal_edges,
    temporal_in_degree,
    temporal_neighbors,
    temporal_nodes,
    temporal_order,
    temporal_out_degree,
    temporal_size,
)
from ..transform import (to_events,
                         to_snapshots,
                         to_static,
                         to_unified)


class TemporalGraph():
    """
    Base class for temporal graphs.

    This class wraps around a NetworkX
    `Graph <https://networkx.org/documentation/stable/reference/classes/graph.html>`__,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__, or
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__,
    depending on the choice of parameters given. It includes most methods implemented by them, such
    as ``add_node``, ``add_edge``, ``remove_node``, ``remove_edge``, ``subgraph``, ``to_directed``,
    and ``to_undirected``, as well as additional methods for handling temporal graphs and temporal
    snapshots.

    .. rubric:: Example

    The following example demonstrates how to create a temporal graph with two snapshots:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalGraph(directed=True, multigraph=True, t=2)
       >>>
       >>> TG[0].add_edge("a", "b")
       >>> TG[1].add_edge("c", "b")
       >>>
       >>> print(TG)

       TemporalMultiDiGraph (t=2) with 4 nodes and 2 edges

    .. hint::

       Setting ``t`` greater than ``1`` will create a list of NetworkX graph objects, each
       representing a snapshot in time. Unless dynamic node attributes are required, it is
       recommended to use the :func:`~networkx_temporal.TemporalGraph.slice` method instead, in order to create less resource-demanding graph
       `views <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
       on the fly.

    .. seealso::

       * The `official NetworkX documentation <https://networkx.org/documentation/stable/reference/classes/index.html>`__
         for a list of methods available for each graph type.
       * The `Examples: Basic operations <https://networkx-temporal.readthedocs.io/en/latest/examples.html>`__
         page for more examples using this class.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.
    :param directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__.
        Defaults to ``False``.
    :param multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__.
        Defaults to ``False``.
    :param object create_using: NetworkX graph object to use as template. Optional.
        Does not allow ``directed`` and ``multigraph`` parameters when set.
    """
    slice = slice
    neighbors = neighbors
    temporal_degree = temporal_degree
    temporal_edges = temporal_edges
    temporal_in_degree = temporal_in_degree
    temporal_neighbors = temporal_neighbors
    temporal_nodes = temporal_nodes
    temporal_order = temporal_order
    temporal_out_degree = temporal_out_degree
    temporal_size = temporal_size
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    def __init__(
        self,
        t: Optional[int] = None,
        directed: bool = None,
        multigraph: bool = None,
        create_using: Optional[Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]] = None,
    ):
        assert t is None or (type(t) == int and t > 0),\
            f"Argument 't' must be a positive integer, received: {t}."

        assert directed is None or type(directed) == bool,\
            f"Argument 'directed' must be a boolean, received: {type(directed)}."

        assert multigraph is None or type(multigraph) == bool,\
            f"Argument 'multigraph' must be a boolean, received: {type(multigraph)}."

        assert create_using is None or type(create_using) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
            f"Argument 'create_using' must be a NetworkX graph object, received: {type(create_using)}."

        assert create_using is None or (directed is None and multigraph is None),\
            "Arguments 'directed' and 'multigraph' are not allowed when 'create_using' is given."

        if create_using is not None:
            directed = create_using.is_directed()
            multigraph = create_using.is_multigraph()

        graph = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")
        self.data = [nx.empty_graph(create_using=graph) for _ in range(t or 1)]

        list(
            self.__setattr__(method, self.__wrapper(method))
            for method in dir(graph)
            if method not in TemporalGraph.__dict__
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

        TG = TemporalGraph(directed=self.directed, multigraph=self.multigraph)
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
               f"{'Multi' if self.multigraph else ''}"\
               f"{'Di' if self.directed else ''}"\
               f"Graph {f'(t={len(self)}) ' if len(self) > 1 else ''}"\
               f"with {sum(self.order())} nodes and {sum(self.size())} edges"

    @property
    def data(self) -> list:
        """
        The ``data`` property of the temporal graph.

        :meta private:
        """
        return self.__dict__.get("_data", None)

    @data.setter
    def data(self, data: Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, list, dict]) -> None:
        """
        The ``data`` property of the temporal graph.

        :param data: NetworkX graph, list or dictionary of NetworkX graphs.

        :meta private:
        """
        assert type(data) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, list, dict),\
            f"Argument 'data' must be a NetworkX graph, list or dictionary, received: {type(data)}."

        data = data if type(data) == list else list(data.values()) if type(data) == dict else [data]

        assert all(type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for G in data),\
                "All elements in data must be valid NetworkX graphs."

        self._data = data

        if type(data) == dict:
            self.names = list(data.keys())

    @property
    def directed(self) -> bool:
        """
        The `directed` property of the temporal graph.

        :meta private:
        """
        return self[0].is_directed()

    @property
    def multigraph(self) -> bool:
        """
        The `multigraph` property of the temporal graph.

        :meta private:
        """
        return self[0].is_multigraph()

    @property
    def name(self) -> str:
        """
        The `name` property of the temporal graph.

        :getter: Returns temporal graph name.
        :setter: Sets temporal graph name.
        :rtype: str
        """
        return self.__dict__.get("_name", "")

    @name.setter
    def name(self, name: Any) -> None:
        """
        The `name` property of the temporal graph.

        :param name: Name to give to temporal graph object.
            If ``None``, resets name to an empty string.
        """
        self.__dict__.pop("_name", None) if name is None else self.__setattr__("_name", name)

    @property
    def names(self) -> list:
        """
        The `name` property of each snapshot in the temporal graph.

        :getter: Returns names of temporal graph snapshots.
        :setter: Sets names of temporal graph snapshots.
        :rtype: list
        """
        return self.__dict__.get("_names", ["" for _ in range(len(self))])

    @names.setter
    def names(self, names: Optional[Union[list, tuple]]) -> None:
        """
        The `name` property of each snapshot in the temporal graph.

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
        Appends a new snapshot to the temporal graph at last position.

        :param G: NetworkX graph to append. Optional.
        """
        self.insert(len(self), G)

    def flatten(self) -> TemporalGraph:
        """
        Returns flattened version of temporal graph. Same as :func:`~networkx_temporal.TemporalGraph.slice` with ``bins=1``.

        .. important::

            A flattened graph does not preserve dynamic node attributes.
        """
        return self.slice(bins=1)

    def insert(self, t: int, G: Optional[nx.Graph] = None) -> None:
        """
        Inserts a new snapshot at a given index.

        :param t: Index of snapshot to insert.
        :param G: NetworkX graph to insert. Optional.
        """
        if G is None:
            G = getattr(nx, f"{'Multi' if self.multigraph else ''}{'Di' if self.directed else ''}Graph")()

        assert type(t) == int,\
            f"Argument 't' must be an integer, received: {type(t)}."

        assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
            f"Argument 'G' must be a valid NetworkX graph, received: {type(G)}."

        assert G.is_directed() == self.is_directed(),\
            f"Received a{' directed' if G.is_directed() else 'n undirected'} graph, "\
            f"but temporal graph is {'not ' if self.is_directed() else ''}directed."

        assert G.is_multigraph() == self.is_multigraph(),\
            f"Received a {'multi' if G.is_multigraph() else ''}graph, "\
            f"but temporal graph is {'' if self.is_multigraph() else 'not '}a multigraph."

        self.data.insert(t, G)

    def index(self, node: Any, interval: Optional[range] = None) -> list:
        """
        Returns index of all snapshots in which a node is present.

        :param node: Node in the temporal graph.
        :param interval: Range to consider. Optional. Defaults to all snapshots.
            Accepts either a ``range`` or a tuple of integers.
        """
        assert interval is None or type(interval) in (range, tuple),\
            "Argument `interval` must be a range or tuple of integers."

        if interval is None:
            interval = range(len(self))

        elif type(interval) == tuple:
            interval = range(*interval)

        return [i for i in (interval or range(len(self))) if self[i].has_node(node)]

    def is_directed(self) -> bool:
        """ Returns directed property of temporal graph. """
        return self.directed

    def is_multigraph(self) -> bool:
        """ Returns multigraph property of temporal graph. """
        return self.multigraph

    def pop(self, t: Optional[int] = None) -> nx.Graph:
        """
        Removes and returns the snapshot at a given time step.

        :param t: Index of snapshot to pop. Default: last snapshot.
        """
        self.__getitem__(t or -1)
        return self.data.pop(t or -1)

    def to_directed(self, as_view: bool = False):
        """
        Returns directed version of temporal graph.

        :param as_view: If ``False``, returns copies instead of views of the original graph.
            Default is ``True``.

        :meta private:
        """
        assert type(as_view) == bool,\
            f"Argument 'as_view' must be either True or False."

        self.data = [G.to_directed(as_view=as_view) for G in self]

        if as_view is False:
            self._directed = True

        return self

    def to_undirected(self, as_view: bool = False):
        """
        Returns undirected version of temporal graph.

        :param as_view: If ``False``, returns copies instead of views of the original graph.
            Default is ``True``.

        :meta private:
        """
        assert type(as_view) == bool,\
            f"Argument 'as_view' must be either True or False."

        self.data = [G.to_undirected(as_view=as_view) for G in self]

        if as_view is False:
            self._directed = False

        return self

    def total_nodes(self) -> int:
        """ Returns total number of nodes in the temporal graph, considering duplicates. """
        return sum(self.order())

    def total_edges(self) -> int:
        """ Returns total number of edges in the temporal graph. Same as ``temporal_size``."""
        return sum(self.size())

    def __wrapper(self, method: str) -> Callable:
        """
        Returns a wrapper function for a given method.

        :meta private:
        """
        def func(*args, **kwargs):
            returns = list(G.__getattribute__(method)(*args, **kwargs) for G in self)
            return returns if any(r is not None for r in returns) else None
        return func


def TemporalDiGraph(t: Optional[int] = None) -> TemporalGraph:
    """
    Alias for the :class:`~networkx_temporal.TemporalGraph`
    class set with ``directed=True`` and ``multigraph=False``.

    This class may optionally be used to create a temporal directed graph.
    """
    return TemporalGraph(t=t, directed=True, multigraph=False)


def TemporalMultiGraph(t: Optional[int] = None) -> TemporalGraph:
    """
    Alias for the :class:`~networkx_temporal.TemporalGraph`
    class set with ``directed=False`` and ``multigraph=True``.

    This class may optionally be used to create a temporal undirected multigraph.
    """
    return TemporalGraph(t=t, directed=False, multigraph=True)


def TemporalMultiDiGraph(t: Optional[int] = None) -> TemporalGraph:
    """
    Alias for the :class:`~networkx_temporal.TemporalGraph`
    class set with ``directed=True`` and ``multigraph=True``.

    This class may optionally be used to create a temporal directed multigraph.
    """
    return TemporalGraph(t=t, directed=True, multigraph=True)
