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

    :param directed: If True, the graph will be a digraph.
    :param multigraph: If True, the graph will be a multigraph.
    :param t: Number of time steps to initialize (optional).
    """
    to_events = to_events
    to_snapshots = to_snapshots
    to_static = to_static
    to_unified = to_unified

    def __init__(self, directed: bool = False, multigraph: bool = False, t: Optional[int] = None) -> None:
        assert t is None or type(t) == int,\
            f"Argument 't' must be an integer, received: {type(t)}."

        assert t is None or t > 0,\
            f"Argument 't' must be greater than zero, received: {t}."

        self.directed = directed
        self.multigraph = multigraph

        self.data = [
            getattr(nx, f"{'Multi' if self.is_multigraph() else ''}{'Di' if self.is_directed() else ''}Graph")()
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

    @property
    def data(self) -> list:
        """ Returns list of snapshots in the temporal graph. """
        return self.__dict__.get("_data", [])

    @data.setter
    def data(self, data: Union[list, dict]) -> None:
        """ Assigns list of snapshots to the temporal graph. """
        assert type(data) in (list, dict),\
            f"Argument 'data' must be a list or dictionary, received: {type(data)}."

        data = data if type(data) == list else list(data.values())

        assert all(type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for G in data),\
                "All elements in data must be valid NetworkX graphs."

        self._data = data

        if type(data) == dict:
            self.names = list(data.keys())

    @property
    def directed(self) -> bool:
        """ Returns directed property from temporal graph. """
        return self.__dict__.get("_directed", None)

    @directed.setter
    def directed(self, value: bool) -> None:
        """ Assigns directed property to temporal graph. """
        assert self.directed is None or not len(self),\
            "Property 'directed' can only be set once. "\
            f"Use `to_{'un' if not self.directed else ''}directed` to convert the graph."

        assert type(value) is bool,\
            "Property 'directed' must be either True or False."

        self._directed = value

    @property
    def multigraph(self) -> bool:
        """ Returns multigraph property from temporal graph. """
        return self.__dict__.get("_multigraph", None)

    @multigraph.setter
    def multigraph(self, value: bool) -> None:
        """ Assigns multigraph property to temporal graph. """
        assert self.multigraph is None,\
               "Property 'multigraph' can only be set once."

        assert type(value) is bool,\
               "Argument 'multigraph' must be either True or False."

        self._multigraph = value

    @property
    def name(self) -> str:
        """ Returns name of temporal graph. """
        return self.__dict__.get("_name", None)

    @name.setter
    def name(self, name: str) -> None:
        """ Assigns name to the temporal graph. """
        self._name = str(name)

    @property
    def names(self) -> list:
        """ Returns names of temporal graph snapshots. """
        names = list(G.name for G in self)
        return names if any(n for n in names) else None

    @names.setter
    def names(self, names: list) -> None:
        """ Returns names of temporal graph snapshots. """
        assert type(names) == list,\
            f"Argument 'names' must be a list, received: {type(names)}."

        assert len(names) == len(self),\
            f"Length of names ({len(names)}) differs from number of snapshots ({len(self)})."

        assert all(type(n) in (str, int) and type(n) == type(names[0]) for n in names),\
            "All elements in names must be either strings or integers."

        assert len(names) == len(set(names)),\
            "All elements in names must be unique."

        list(setattr(self.data[t], "name", names[t]) for t in range(len(self)))

    @property
    def t(self) -> int:
        """ Returns number of time steps in the temporal graph. """
        return len(self)

    def append(self, G: Optional[nx.Graph] = None) -> nx.Graph:
        """ Appends a new snapshot to the temporal graph. """
        self.insert(len(self), G)

    def insert(self, t: int, G: Optional[nx.Graph] = None) -> nx.Graph:
        """ Inserts a new snapshot at a given time step. """
        if G is None:
            G = self._empty_graph()

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

    def pop(self, t: Optional[int] = None) -> nx.Graph:
        """ Removes and returns the snapshot at a given time step. """
        self.__getitem__(t or -1)
        return self.data.pop(t or -1)

    def slice(
        self,
        bins: Optional[Union[int, bool]] = None,
        attr: Optional[Union[str, list, dict]] = None,
        attr_level: Optional[Literal["node", "edge"]] = None,
        node_level: Optional[Literal["source", "target"]] = None,
        qcut: bool = False,
        duplicates: bool = False,
        rank_first: Optional[bool] = None,
        sort: bool = True,
        fillna: Optional[Any] = None,
        apply_func: Optional[Callable[..., Any]] = None,
    ) -> list:
        """
        Slices temporal graph into time bins, returning a new temporal graph object.

        Contrary to `nx.{edge_,}subgraph`, this method returns a copy instead of a view,
        allowing further manipulation without affecting the original graph object.

        Note that no data is lost when using this method, as it includes all nodes and
        edges from the original graph, plus additional features such as data binning.

        :param bins: Number of slices to create, or True to consider all unique time values.
        :param attr: Node- or edge-level attribute to consider as temporal data.
        :param attr_level: Level of temporal attribute, either 'node' or 'edge'.
        :param node_level: Level of temporal nodes to consider, either 'source' or 'target'.
        :param qcut: If True, use quantiles to obtain time bins.
        :param duplicates: If False, raise an error when time bins contain duplicates.
        :param rank_first: If True, rank data points before slicing.
        :param sort: If True, sort unique time values after slicing.
        :param fillna: Value to fill null values in attribute data.
        :param apply_func: Function to apply to time attribute values.
        """
        assert self.data,\
            "Temporal graph is empty."

        assert sum(self.order()),\
            "Temporal graph has no nodes."

        assert sum(self.size()),\
            "Temporal graph has no edges."

        # Set default slicing method (edge-level attribute data).
        if attr is None:
            if attr_level is None:
                attr_level = "edge"
            if bins is None:
                bins = True
            if rank_first is None and len(self) == 1:
                rank_first = True

        # Set default temporal node (node-level attribute data).
        if attr_level == "node" and node_level is None:
            node_level = "source"

        # Check if attribute data is valid.
        assert attr is None or type(attr) in (str, list, dict, pd.Series, pd.DataFrame),\
            f"Argument `attr` accepts a str, list, dict, pandas Series or DataFrame, received: {type(attr)}."

        assert type(attr) != str or attr_level in ("node", "edge"),\
            f"Argument `attr_level` must be either 'node' or 'edge' when `attr` is a string."

        assert node_level is None or attr_level == "node",\
            f"Argument `node_level` is not applicable to edge-level attribute data."

        assert node_level in ("source", "target") or attr_level != "node",\
            f"Argument `node_level` must be either 'source' or 'target' when slicing node-level attribute data."

        assert bins in (None, True, False) or bins > 0,\
            f"Argument `bins` must be positive integer or True."

        # Obtain static graph object and edge data.
        G = self.to_static()
        edges = nx.to_pandas_edgelist(G)
        names = None

        # Obtain temporal data from node-level or edge-level attributes.
        if type(attr) == str:
            times = pd.Series(
                [_[-1] for _ in getattr(G, f"{attr_level}s")(data=attr)],
                index=G.nodes() if attr_level == "node" else None
            )

        elif type(attr) == list:
            times = pd.Series(attr, index=G.nodes() if attr_level == "node" else None)

        elif type(attr) == dict:
            times = pd.Series(attr)

        elif type(attr) == pd.Series:
            times = attr

        elif type(attr) == pd.DataFrame:
            times = attr.squeeze()

        else:
            times = pd.Series(
                [t for t, size in enumerate(self.size()) for _ in range(size)]
                if attr_level == "edge" else
                [t for t, order in enumerate(self.order()) for _ in range(order)]
            )

        # Check if attribute data has the right length.
        assert attr_level == "node" or len(times) == G.size(),\
            f"Length of `attr` ({len(times)}) differs from number of edges ({G.size()})."

        assert attr_level == "edge" or len(times) == G.order(),\
            f"Length of `attr` ({len(times)}) differs from number of nodes ({G.order()})."

        # Fill null values in attribute data.
        if times.isna().any():
            assert not times.isna().all(),\
                f"Attribute does not exist or contains null values only."

            assert fillna is not None,\
                f"Found null value(s) in attribute data, but `fillna` has not been set."

            times.fillna(fillna, inplace=True)

        # Apply function to time attribute values.
        if apply_func is not None:
            times = times.apply(apply_func)

        # Obtain edge temporal values from node-level data [0/1].
        if attr_level == "node":
            times = edges[node_level].apply(times.get)

        # Return a given number of time bins.
        if bins:

            # Consideer unique time values from attribute data.
            if bins is True:
                bins = len(times.unique())

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

            # Slice data in a given nuber of time steps.
            if type(bins) == int:

                # Factorize to ensure strings can be binned,
                # e.g., sortable dates in 'YYYY-MM-DD' format.
                if times.dtype.__str__() == "object":
                    factorize, names = pd.factorize(times, sort=sort)
                    times = pd.Series(factorize, index=times.index)

                # Bin data points into time intervals.
                times = getattr(pd, "qcut" if qcut else "cut")(
                    times,
                    bins,
                    duplicates="drop" if duplicates is False else "raise",
                )

                # Convert categorical time bins to string intervals.
                if names is None:
                    names = [c.__str__()
                             for c in times.cat.categories
                             if c in set(times.unique())]
                else:
                    names = [f"{'[' if c.closed_left else '('}{names[int(c.left)]}, "
                             f"{names[int(c.right)]}{']' if c.closed_right else ')'}"
                             for c in times.cat.categories
                             if c in set(times.unique())]

            # Obtain edge temporal values from node-level data [1/1].
            if node_level:
                times = edges[node_level].apply(times.get)

        # Group edge indices by time.
        indices = edges.groupby(times, observed=False).groups

        # Create temporal subgraphs with node attributes.
        graphs = [
            nx.create_empty_copy(
                G.subgraph(
                    edges
                    .iloc[index]
                    .apply(lambda e: (e["source"], e["target"]), axis=1)
                    .explode()
                )
            )
            for index in
                indices.values()
        ]

        # Add edges with attributes to created subgraphs.
        list(
            graphs[t].add_edges_from(
                edges
                .iloc[index]
                .apply(
                    lambda e: (
                        e["source"],
                        e["target"],
                        {k: v for k, v in e.items() if k not in ("source", "target")}
                    ),
                    axis=1
                )
            )
            for t, index in
                enumerate(indices.values())
        )

        # Create new temporal graph object.
        TG = TemporalGraph(directed=self.directed, multigraph=self.multigraph)
        TG.data = graphs
        TG.names = names or list(indices.keys())
        return TG

    def to_directed(self, as_view: bool = False):
        """
        Returns directed version of temporal graph.

        :param as_view: If True, returns a view of the original graph.
            Default is False.
        """
        assert as_view in (True, False),\
            f"Argument 'as_view' must be either True or False."

        self.data = [G.to_directed(as_view=as_view) for G in self]

        if as_view is False:
            self._directed = True

        return self

    def to_undirected(self, as_view: bool = False):
        """
        Returns undirected version of temporal graph.

        :param as_view: If True, returns a view of the original graph.
            Default is False.
        """
        assert as_view in (True, False),\
            f"Argument 'as_view' must be either True or False."

        self.data = [G.to_undirected(as_view=as_view) for G in self]

        if as_view is False:
            self._directed = False

        return self

    def _edge_coupling_index(self, v: str, interval: range) -> int:
        """ Returns index of next appearance for a given node. """
        return next(iter([i for i in interval if self[i].has_node(v)]))

    def __wrapper(self, method: str) -> Callable:
        """ Returns a wrapper function for a given method. """
        def func(*args, **kwargs):
            returns = list(G.__getattribute__(method)(*args, **kwargs) for G in self)
            return returns if any(r is not None for r in returns) else None
        return func

    is_directed = lambda self: self.directed
    is_multigraph = lambda self: self.multigraph

    neighbors = lambda self, v:\
        list(list(G.neighbors(v)) if G.has_node(v) else [] for G in self)

    temporal_neighbors = lambda self, v:\
        reduce(or_, iter(set(N) for N in self.neighbors(v)))

    temporal_degree = lambda self, *args, **kwargs:\
        reduce(reduce_sum, self.degree(*args, **kwargs))

    temporal_in_degree = lambda self, *args, **kwargs:\
        reduce(reduce_sum, self.in_degree(*args, **kwargs))

    temporal_out_degree = lambda self, *args, **kwargs:\
        reduce(reduce_sum, self.out_degree(*args, **kwargs))

    temporal_index = lambda self, v: [t for t in range(len(self)) if self[t].has_node(v)]
    temporal_nodes = lambda self: reduce(or_, self.nodes(data=False))
    temporal_edges = lambda self: list(e for E in self.edges() for e in E)

    temporal_order = lambda self: len(self.temporal_nodes())
    temporal_size = lambda self: sum(self.size())

    total_nodes = lambda self: sum(self.order())
    total_edges = temporal_size


def reduce_sum(d1: Union[int, dict], d2: Union[int, dict]):
    """ Returns sum of two integers or dictionaries. """
    if type(d1) == int or type(d2) == int:
        return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)

    d1, d2 = dict(d1), dict(d2)
    return {v: d1.get(v, 0) + d2.get(v, 0) for v in set(d for d in d1|d2)}
