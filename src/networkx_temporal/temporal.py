from __future__ import annotations

from functools import reduce
from operator import or_
from typing import Any, Callable, Literal, Optional, Union

import networkx as nx
import pandas as pd

from .transform.events import to_events
from .transform.snapshots import to_snapshots
from .transform.static import to_static
from .transform.unified import to_unified


class TemporalGraph():
    """
    Base class for temporal graphs.

    This class is a wrapper around NetworkX's `Graph
    <https://networkx.org/documentation/stable/reference/classes/graph.html>`_,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`_,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_
    and
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`_
    classes, and includes most methods from NetworkX's graph classes, such as `add_node`, `add_edge`,
    `remove_node`, `remove_edge`, `neighbors`, `degree`, `in_degree`, `out_degree`, `subgraph`, `copy`,
    `to_directed`, `to_undirected`, among others.
    The default graph type if no parameters are given is a
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.

    For a full list of methods available, please refer to NetworkX's documentation.

    :param directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`_.
        Default is ``False``.
    :param multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.
        Default is ``True``.
    :param t: Number of time steps to initialize.
        Default is ``1``.

    .. note::

        Setting a number of time steps greater than ``1`` will create a list of NetworkX graph objects,
        each representing a snapshot in time. Alternatively, the
        `slice <#networkx_temporal.TemporalGraph.slice>`_ method can be used to create
        less resource-demanding graph views on-the-fly (see
        `Get started: Slice temporal graph <./guide.html#slice-temporal-graph>`__).

    """
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    def __init__(self, directed: bool = False, multigraph: bool = True, t: Optional[int] = 1):
        assert type(directed) == bool,\
            f"Argument 'directed' must be a boolean, received: {type(directed)}."

        assert type(multigraph) == bool,\
            f"Argument 'multigraph' must be a boolean, received: {type(multigraph)}."

        assert t is None or (type(t) == int and t > 0),\
            f"Argument 't' must be a positive integer, received: {t}."

        self.data = [
            getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()
            for t in range(t or 1)
        ]

        list(
            self.__setattr__(method, self.__wrapper(method))
            for method in [
                m for m in dir(self.data[0])
                if not m.startswith("_")
                and m not in TemporalGraph.__dict__
            ]
        )

    def __getitem__(self, t: Union[str, int, slice]) -> nx.Graph:
        """ Returns snapshot from a given interval. """
        assert self.data,\
            "Temporal graph is empty."

        assert type(t) in (str, int, slice),\
            f"Parameter must be a str, integer or slice, received: {type(t)}."

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
               f"{'Multi' if self.is_multigraph() else ''}"\
               f"{'Di' if self.directed else ''}"\
               f"Graph (t={len(self)}) "\
               f"with {sum(self.order())} nodes and {sum(self.size())} edges"

    def slice(
        self,
        bins: Optional[int] = None,
        attr: Optional[Union[str, list, dict, pd.DataFrame, pd.Series]] = None,
        attr_level: Optional[Literal["node", "edge"]] = None,
        node_level: Optional[Literal["source", "target"]] = None,
        qcut: bool = False,
        duplicates: Literal["raise", "drop"] = "raise",
        rank_first: Optional[bool] = None,
        sort: bool = True,
        as_view: bool = True,
        fillna: Optional[Any] = None,
        apply_func: Optional[Callable[..., Any]] = None,
    ) -> TemporalGraph:
        """
        Slices temporal graph into snapshots, returning a new temporal graph object.

        See `Get started: Slice temporal graph <#slice-temporal-graph>`_ for examples.

        .. note::

            No data is lost when using this method, as it includes all nodes and edges from
            the original graph. However, the method may return duplicate nodes, if connected
            to others in multiple snapshots; and edges, if ``duplicates`` is not set to ``'raise'``.

        :param bins: Number of snapshots (slices) to return.
            If unset, the method will consider unique values from ``attr``.
            Required if ``attr`` is unset.
        :param attr: Node- or edge-level attribute to
            consider as temporal data. If unset, the method will consider the order of appearance of
            edges or nodes.
        :param attr_level: Level of temporal attribute, either ``'node'`` or ``'edge'``.
            Required if ``attr`` is a string. Defaults to ``'edge'`` if unset.
        :param node_level: Level of temporal nodes to consider, either 'source' or 'target'.
            Required if `attr_level` is 'node'. Defaults to ``'source'`` if unset.
        :param qcut: If ``True``, use quantiles to obtain snapshots.
            Default is ``False``.
        :param duplicates: Control whether slices containing duplicates raise an error.
            Accepts ``'drop'`` or ``'raise'``. Default is ``'raise'``.
        :param rank_first: If `True`, rank data points before slicing.
            Automatically set to True if temporal data is categorical.
        :param sort: If `True`, sort unique temporal values after slicing.
            Only applies to categorical temporal data. Defualt is ``True``.
        :param as_view: If ``False``, returns copies instead of views of the original graph.
            Default is ``True``.
        :param fillna: Value to fill null values in attribute data.
        :param apply_func: Function to apply to temporal attribute values.
        """
        assert self.data, "Temporal graph is empty."
        assert sum(self.order()), "Temporal graph has no nodes."
        assert sum(self.size()), "Temporal graph has no edges."

        # Set default slicing method (by order of appearance of edges).
        if attr is None:
            attr_level = attr_level if attr_level is not None else "edge"
            rank_first = rank_first if rank_first is not None else True

        # Automatically set `attr_level` if attribute data is not a string.
        elif type(attr) != str:
            length = getattr(attr, "__len__", lambda: None)()

            assert length is not None,\
                f"Attribute data must be a list, dictionary or sequence of elements, received: {type(attr)}."

            assert attr_level is not None or not length == self.temporal_order() == self.temporal_size(),\
                "Attribute level must be set for graphs with the same number of nodes and edges."

            attr_level = "node" if length == self.temporal_order() else "edge"

        # Set default attribute level (edge or source if node-level).
        if attr is not None and attr_level is None:
            attr_level = "edge"

        elif attr_level == "node" and node_level is None:
            node_level = "source"

        # Check if arguments are valid.
        assert attr is not None or bins is not None,\
            "Argument `bins` must be set if `attr` is unset."

        assert bins is None or (type(bins) == int and bins > 0),\
            "Argument `bins` must be positive integer if set."

        assert type(attr) != str or attr_level in ("node", "edge"),\
            "Argument `attr_level` must be either 'node' or 'edge' when `attr` is a string."

        assert node_level is None or attr_level == "node",\
            "Argument `node_level` is not applicable to edge-level attribute data."

        assert node_level in ("source", "target") or attr_level != "node",\
            "Argument `node_level` must be either 'source' or 'target' when slicing node-level attribute data."

        # Obtain static graph object and edge data.
        G = self.to_static()
        edges = pd.DataFrame(G.edges(keys=True) if self.is_multigraph() else G.edges())
        names = None

        # Obtain node- or edge-level attribute data.
        if attr is None:
            times = pd.Series(
                range(G.size() if attr_level == "edge" else G.order()),
                index=G.nodes() if attr_level == "node" else None
            )

        elif type(attr) == str:
            times = pd.Series(
                [_[-1] for _ in getattr(G, f"{attr_level}s")(data=attr)],
                index=G.nodes() if attr_level == "node" else None
            )

        elif type(attr) == dict:
            times = pd.Series(attr)

        elif type(attr) == pd.DataFrame:
            times = attr.squeeze()

        else:
            times = pd.Series(attr, index=G.nodes() if attr_level == "node" else None)

        # Check if attribute data has the right length.
        assert attr_level == "node" or len(times) == G.size(),\
            f"Length of `attr` ({len(times)}) differs from number of edges ({G.size()})."

        assert attr_level == "edge" or len(times) == G.order(),\
            f"Length of `attr` ({len(times)}) differs from number of nodes ({G.order()})."

        # Fill null values in attribute data.
        if times.isna().any():
            assert not times.isna().all(),\
                f"Attribute does not exist at {attr_level} level or contains null values only."

            assert fillna is not None,\
                f"Found null value(s) in attribute data, but `fillna` has not been set."

            times.fillna(fillna, inplace=True)

        # Apply function to time attribute values.
        if apply_func is not None:
            times = times.apply(apply_func)

        # Select node-level column by position.
        if attr_level == "node":
            if node_level in (None, "source"):
                node_level = 0
            elif node_level == "target":
                node_level = 1

        # Obtain edge temporal values from node-level data [0/1].
        if attr_level == "node":
            times = edges[node_level].apply(times.get)

        # Obtain node-wise (source or target) cut to consider for time bins.
        if node_level:
            times = [
                pd.Series(
                    times.loc[nodes.index].values,
                    index=nodes.values
                )
                for nodes in (
                    [edges[node_level].drop_duplicates().sort_values()]
                )
            ][0]

        # Treat data points sequentially.
        if rank_first:
            times = times.rank(method="first")

        # Consider unique time values from attribute data.
        if not bins:
            bins = len(times.unique())

        # Slice data in a given nuber of time steps.
        bins = min(bins or 0, len(times.unique()))

        # Factorize to ensure strings can be binned,
        # e.g., sortable dates in 'YYYY-MM-DD' format.
        if times.dtype.__str__() == "object":
            factorize, names = pd.factorize(times, sort=sort)
            times = pd.Series(factorize, index=times.index)

        # Bin data points into time intervals.
        times = getattr(pd, "qcut" if qcut else "cut")(
            times,
            bins,
            duplicates=duplicates,
        )\
        .cat\
        .remove_unused_categories()

        # Convert categories to string intervals.
        names = [f"{'[' if c.closed_left else '('}"
                 f"{c.left if names is None else names[int(c.left)]}, "
                 f"{c.right if names is None else names[int(c.right)]}"
                 f"{']' if c.closed_right else ')'}"
                 for c in times.cat.categories]

        # Obtain edge temporal values from node-level data.
        if node_level:
            times = edges[node_level].apply(times.get)

        # Group edge indices by time.
        indices = edges.groupby(times, observed=False).groups

        # Create temporal graph snapshots.
        graphs = [
            G.edge_subgraph(
                edges
                .iloc[index]
                .apply(lambda e: (e[0], e[1], e[2]) if self.is_multigraph() else (e[0], e[1]), axis=1)
            )
            for index in indices.values()
        ]

        # Create copies instead of views.
        if not as_view:
            graphs = [G.copy() for G in graphs]

        # Create new temporal graph object.
        TG = TemporalGraph(directed=self.directed, multigraph=self.multigraph)
        TG.data = graphs
        TG.name = self.name
        TG.names = names
        return TG

    @property
    def data(self) -> list:
        """
        Temporal graph ``data`` property.

        :meta private:
        """
        return self.__dict__.get("_data", None)

    @data.setter
    def data(self, data: Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, list, dict]) -> None:
        """
        Sets data as graph or list of graph objects.

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
        Temporal graph ``directed`` property.

        :meta private:
        """
        return self[0].is_directed()

    @property
    def multigraph(self) -> bool:
        """
        Temporal graph ``multigraph`` property.

        :meta private:
        """
        return self[0].is_multigraph()

    @property
    def name(self) -> str:
        """
        Temporal graph ``name`` property.

        :getter: Returns temporal graph name.
        :setter: Sets temporal graph name.
        :rtype: str|None
        """
        return self.__dict__.get("_name", None)

    @name.setter
    def name(self, name: str) -> None:
        """
        Sets name of temporal graph.

        :param name: Name to give to temporal graph object.
        """
        self._name = str(name)

    @property
    def names(self) -> list:
        """
        Returns names of temporal graph snapshots.

        :getter: Returns names of temporal graph snapshots.
        :setter: Sets names of temporal graph snapshots.
        :rtype: str|None
        """
        return self.__dict__.get("_names", [None for _ in range(len(self))])

    @names.setter
    def names(self, names: Union[list, tuple]) -> None:
        """
        Sets names of temporal graph snapshots.

        :param names: Names to give to temporal graph snapshots.
        """
        assert type(names) in (list, tuple),\
            f"Argument 'names' must be a list or tuple, received: {type(names)}."

        assert len(names) == len(self),\
            f"Length of names ({len(names)}) differs from number of snapshots ({len(self)})."

        assert all(type(n) in (str, int) and type(n) == type(names[0]) for n in names),\
            "All elements in names must be either strings or integers."

        assert len(names) == len(set(names)),\
            "All elements in names must be unique."

        # NOTE: Does not work if graphs are views.
        # list(setattr(self[t], "name", names[t]) for t in range(len(self)))

        self._names = list(names)

    def append(self, G: Optional[nx.Graph] = None) -> nx.Graph:
        """
        Appends a new snapshot to the temporal graph at last position.

        :param G: NetworkX graph to append. Optional.
        """
        self.insert(len(self), G)

    def flatten(self) -> TemporalGraph:
        """ Returns flattened version of temporal graph. Same as ``slice(bins=1)``."""
        return self.slice(bins=1)

    def insert(self, t: int, G: Optional[nx.Graph] = None) -> nx.Graph:
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

    def is_directed(self) -> bool:
        """ Returns directed property from temporal graph. """
        return self.directed

    def is_multigraph(self) -> bool:
        """ Returns multigraph property from temporal graph. """
        return self.multigraph

    def pop(self, t: Optional[int] = None) -> nx.Graph:
        """
        Removes and returns the snapshot at a given time step.

        :param t: Index of snapshot to pop.
        """
        self.__getitem__(t or -1)
        return self.data.pop(t or -1)

    def to_directed(self, as_view: bool = False):
        """
        Returns directed version of temporal graph.

        :param as_view: If ``False``, returns copies instead of views of the original graph.
            Default is ``True``.
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
        """
        assert type(as_view) == bool,\
            f"Argument 'as_view' must be either True or False."

        self.data = [G.to_undirected(as_view=as_view) for G in self]

        if as_view is False:
            self._directed = False

        return self

    def temporal_neighbors(self, v: Any) -> dict:
        """
        Returns neighbors of a node in all snapshots.

        :param v: Node in the graph.
        """
        return reduce(or_, iter(set(N) for N in self.neighbors(v)))

    def temporal_degree(self, *args, **kwargs) -> dict:
        """ Returns degree of a node in all snapshots. """
        return reduce(reduce_sum, self.degree(*args, **kwargs))

    def temporal_in_degree(self, *args, **kwargs) -> dict:
        """ Returns in-degree of a node in all snapshots. """
        return reduce(reduce_sum, self.in_degree(*args, **kwargs))

    def temporal_out_degree(self, *args, **kwargs) -> dict:
        """ Returns out-degree of a node in all snapshots. """
        return reduce(reduce_sum, self.out_degree(*args, **kwargs))

    def temporal_index(self, v: Any) -> list:
        """
        Returns all snapshots where a node appears.

        :param v: Node in the graph.
        """
        return [t for t in range(len(self)) if self[t].has_node(v)]

    def temporal_nodes(self) -> list:
        """ Returns all nodes in all snapshots. """
        return reduce(or_, self.nodes(data=False))

    def temporal_edges(self) -> list:
        """ Returns all edges in all snapshots. """
        return list(e for E in self.edges() for e in E)

    def temporal_order(self) -> int:
        """ Returns total number of nodes (without duplicates) in the temporal graph. """
        return len(self.temporal_nodes())

    def temporal_size(self) -> int:
        """ Returns total number of edges in the temporal graph. Same as ``total_edges``."""
        return sum(self.size())

    def total_nodes(self):
        """ Returns total number of nodes (with duplicates) in the temporal graph. """
        return sum(self.order())

    def total_edges(self):
        """ Returns total number of edges in the temporal graph. Same as ``temporal_size``."""
        return sum(self.size())

    def _edge_coupling_index(self, v: str, interval: range) -> int:
        """ Returns index of next appearance for a given node. """
        return next(iter([i for i in interval if self[i].has_node(v)]))

    def __wrapper(self, method: str) -> Callable:
        """ Returns a wrapper function for a given method. """
        def func(*args, **kwargs):
            returns = list(G.__getattribute__(method)(*args, **kwargs) for G in self)
            return returns if any(r is not None for r in returns) else None
        return func

    neighbors = lambda self, v:\
        list(list(G.neighbors(v)) if G.has_node(v) else [] for G in self)


def reduce_sum(d1: Union[int, dict], d2: Union[int, dict]):
    """ Returns sum of two integers or dictionaries. """
    if type(d1) == int or type(d2) == int:
        return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)

    d1, d2 = dict(d1), dict(d2)
    return {v: d1.get(v, 0) + d2.get(v, 0) for v in set(d for d in {**d1, **d2})}
