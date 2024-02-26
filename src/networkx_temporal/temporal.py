from abc import ABCMeta, abstractmethod
from functools import reduce
from typing import Any, Callable, Literal, Optional, Union

import networkx as nx
import pandas as pd


class TemporalBase(metaclass=ABCMeta):
    """
    Base class for temporal graphs.

    :param directed: If True, the graph will be directed.
    :param multigraph: If True, the graph will be a multigraph.
    :param t: Number of time steps to initialize (optional).
    """
    @abstractmethod
    def __init__(
        self,
        directed: bool,
        multigraph: bool,
        t: Optional[int] = None,
    ) -> None:
        """ Initializes a temporal graph. """
        assert t is None or type(t) == int,\
               f"Argument 't' must be an integer, received: {type(t)}."

        assert t is None or t > 0,\
               f"Argument 't' must be greater than zero, received: {t}."

        self.directed = directed
        self.multigraph = multigraph

        self.data = [
            self._empty_graph()
            for t in range(t or 1)
        ]

        list(
            self.__setattr__(method, self.__wrapper(method))
            for method in [
                m for m in dir(self.data[0] if len(self) else self._empty_graph())
                if not m.startswith("_")
                and m not in TemporalBase.__dict__
            ]
        )

    def __getitem__(self, t: Union[str, int, slice]) -> nx.Graph:
        """ Returns temporal graph from a given interval. """
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

        TG = empty_graph(create_using=self)
        TG.data = self.data[t]
        return TG

    def __iter__(self) -> iter:
        """ Returns iterator over slices in the temporal graph. """
        return iter(self.data)

    def __len__(self) -> int:
        """ Returns number of slices in the temporal graph. """
        return len(self.data)

    def __new__(cls, *args, **kwargs) -> Any:
        """ Creates a new instance of the temporal graph. """
        if cls is TemporalBase:
            raise TypeError(f"{cls.__name__} cannot be instantiated.")

        return super().__new__(cls)

    def __repr__(self) -> str:
        """ Returns string representation of the temporal graph. """
        return f"{type(self).__name__}(t={len(self)})"

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
        return self.__dict__.get("_name", "")

    @name.setter
    def name(self, name: str) -> None:
        """ Assigns name to the temporal graph. """
        self._name = name

    @property
    def names(self) -> list:
        """ Returns names of temporal graph snapshots. """
        names = list(G.name for G in self)
        return names if any(n != '' for n in names) else None

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
        list(
            setattr(self.data[t], "name", names[t])
            for t in range(len(self))
        )

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
            if rank_first is None:
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
                    times, names = pd.factorize(times, sort=sort)

                # Bin data points into time intervals.
                times = getattr(pd, "qcut" if qcut else "cut")(
                    times,
                    bins,
                    duplicates="drop" if duplicates is False else "raise",
                )

                # Convert categorical time bins to named intervals.
                if names is not None:
                    names = [
                        f"{'[' if c.closed_left else '('}{names[int(c.left)]}, {names[int(c.right)]}{']' if c.closed_right else ')'}"
                        for c in times.categories
                    ]

            # Obtain edge temporal values from node-level data [1/1].
            if node_level:
                times = edges[node_level].apply(times.get)

        # Convert categorical time bins to string intervals.
        if type(times.dtype) == pd.core.dtypes.dtypes.CategoricalDtype:
            names = [c.__str__() for c in times.cat.categories]

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
        TG = empty_graph(create_using=self)
        TG.data = graphs
        TG.names = names or list(indices.keys())
        return TG

    def to_directed(self):
        """ Returns directed version of the temporal graph. """
        TG = empty_graph(directed=True, multigraph=self.is_multigraph())
        TG.data = [G.to_directed() for G in self]
        return TG

    def to_undirected(self):
        """ Returns undirected version of the temporal graph. """
        TG = empty_graph(directed=False, multigraph=self.is_multigraph())
        TG.data = [G.to_directed() for G in self]
        return TG

    def to_events(self, stream: bool = True) -> list:
        """
        Returns a sequence of events, e.g., (u, v, t), where u and v are nodes
        and t specifies the time of the event, or (u, v, t, e), where e is either
        an edge addition if a positive unit (1) or deletion if a negative unit (-1).

        **Note**: as sequences of events are edge-based, node isolates are not preserved.

        :param stream: If `False`, returns events as 4-tuples, i.e., (u, v, t, e).
        """
        if stream:
            return [(e[0], e[1], t) for t, G in enumerate(self) for e in G.edges()]

        events = []
        for t in range(len(self)):
            if t == 0:
                for edge in self[0].edges():
                    events.append((*edge, t, 1))
            else:
                for edge in self[t].edges():
                    if not self[t-1].has_edge(*edge):
                        events.append((*edge, t, 1))
                for edge in self[t-1].edges():
                    if not self[t].has_edge(*edge):
                        events.append((*edge, t, -1))

        return events

    def to_snapshots(self) -> list:
        """
        Returns a sequence of snapshots where each slice represent the state
        of the network at a given time, i.e., a list of NetworkX graphs.

        Internally, the TemporalGraph class already stores its data as a list of
        graphs, so this method simply returns the object itself (`self._data`).
        """
        return self.data

    def to_static(self, attr_name: Optional[str] = None) -> nx.Graph:
        """
        Returns a static multigraph from a temporal graph.

        A static multigraph is a single object containing all nodes and
        edges of a temporal graph concatenated in a single object.

        **Note**: as each node is unique, dyanamic node attributes from
        the temporal graph are not preserved in the static multigraph.

        :param attr_name: Edge attribute name to store time (optional).
        """
        assert attr_name not in next(iter(self[0].edges(data=True)))[2],\
                f"Edge attribute '{attr_name}' already exists in graph."

        G = getattr(nx, f"Multi{'Di' if self.is_directed() else ''}Graph")()

        list(G.add_nodes_from(nodes)
             for nodes in self.nodes(data=True))

        list(G.add_edges_from(
             [(e[0], e[1], e[2] if not attr_name else e[2]|{attr_name: t}) for e in edges])
             for t, edges in enumerate(self.edges(data=True)))

        return G

    def to_unified(
        self,
        add_couplings: bool = True,
        add_proxy_nodes: bool = True,
        proxy_nodes_with_attr: bool = True,
        prune_proxy_nodes: bool = True,
        node_index: list = None,
    ) -> nx.Graph:
        """
        Returns unified temporal graph (UTG) from snapshot temporal graph (STG).

        The UTG is a single graph that contains all the nodes and edges of an STG,
        plus proxy nodes and edge couplings connecting sequential temporal nodes.

        :param add_couplings: Add inter-slice couplings among temporal nodes.
        :param add_proxy_nodes: Add proxy nodes on subsequent slices.
        :param proxy_nodes_with_attr: Include proxy nodes with attributes.
        :param prune_proxy_nodes: Prune proxy nodes from subsequent slices.
        :param node_index: Node index to include as attribute.
        """
        T = range(len(self))

        # Create graph with intra-slice nodes and edges,
        # relabeling nodes to include temporal index.
        UTG = nx.compose_all([
            nx.relabel_nodes(
                self[t],
                {v: f"{v}_{t}" for v in self[t].nodes()}
            )
            for t in T
        ])

        # Add attributed proxy nodes on sebsequent slices.
        if add_proxy_nodes:
            proxy_nodes = self._proxy_nodes(self, prune_proxy_nodes)
            # Compose attributed graph containing node isolates only.
            if proxy_nodes_with_attr:
                G = nx.compose_all(
                    nx.create_empty_copy(
                        self[t].subgraph(nodes)
                    )
                    for t, nodes in {
                        t: [
                            node
                            for node, interval in proxy_nodes.items()
                            if interval[0] == t
                        ]
                        for t in T
                    }
                    .items()
                )
            # Include proxy nodes in unified temporal graph.
            list(
                (
                    UTG := nx.compose(
                        UTG,
                        nx.relabel_nodes(
                            G.subgraph(nodes),
                            {v: f"{v}_{t}" for v in nodes}
                        )
                    )
                )
                if proxy_nodes_with_attr else
                    UTG.add_nodes_from(
                        [f"{v}_{t}" for v in nodes]
                    )
                for t, nodes in {
                    t: [
                        node
                        for node, interval in proxy_nodes.items()
                        if t in range(interval[0]+1, interval[1]+1)
                        and not self[t].has_node(node)
                    ]
                    for t in T
                }
                .items()
            )

        # Add inter-slice couplings among temporal nodes.
        if add_couplings:
            UTG.add_edges_from(
                self._couplings(
                    self,
                    proxy_nodes if add_proxy_nodes else None
                )
            )

        # Add temporal node indices as attributes.
        if node_index:
            node_index = [str(v) for v in node_index]

            assert len(node_index) == len(set(node_index)),\
                    "Repeated node indices are not allowed "\
                    "(are there strings and integers used as labels?)."

            nx.set_node_attributes(
                UTG,
                {
                    node: {
                        "index": node_index.index(node.rsplit("_", 1)[0]),
                    }
                    for node in UTG.nodes()
                }
            )

        return UTG

    @staticmethod
    def _couplings(STG: Union[dict, list], proxy_nodes: Optional[dict] = None) -> set:
        """
        Returns set of edges couplings from a snapshot temporal graph (STG).

        A coupling is an edge connecting two nodes from different time steps.
        """
        T = list(STG.keys() if type(STG) == dict else range(len(STG)))

        couplings = set()
        for i in range(len(T)-1):
            for node in STG[T[i]].nodes():
                for j in range(i+1, len(T)):
                    if STG[T[j]].has_node(node)\
                    or ((proxy_nodes or {}).get(node) and j-1 in range(*proxy_nodes.get(node))):
                        couplings.add((f"{node}_{T[i]}", f"{node}_{T[j]}"))
                        break

        if proxy_nodes:
            list(
                couplings.add((f"{node}_{T[t-1]}", f"{node}_{T[t]}"))
                for node, bounds in proxy_nodes.items()
                for t in range(bounds[0]+1, bounds[1]+1)
            )

        return couplings

    @staticmethod
    def _proxy_nodes(STG: Union[dict, list], prune: bool = True) -> dict:
        """
        Returns dictionary of proxy nodes from a snapshot temporal graph (STG).

        A proxy node is a node that exists in a previous time step and is used
        to represent a node that does not exist in a subsequent time step.
        """
        T = list(STG.keys() if type(STG) == dict else range(len(STG)))

        proxy_nodes = {}
        for i in range(len(T)-1):
            for node in STG[T[i]].nodes():
                if not proxy_nodes.get(node):
                    for j in reversed(range(min(i+2, len(T)), len(T))):
                        if STG[T[j]].has_node(node) or not prune:
                            proxy_nodes[node] = (i, j)
                            break

        return proxy_nodes

    def _empty_graph(self) -> nx.Graph:
        """ Returns empty graph of the same type. """
        return getattr(nx, f"{'Multi' if self.is_multigraph() else ''}{'Di' if self.is_directed() else ''}Graph")()

    def __wrapper(self, method) -> Callable:
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
        list(set(n for G in self if G.has_node(v) for N in G.neighbors(v) for n in N))

    temporal_degree = lambda self, *args, **kwargs:\
        reduce(_reduce_sum, self.degree(*args, **kwargs))

    temporal_in_degree = lambda self, *args, **kwargs:\
        reduce(_reduce_sum, self.in_degree(*args, **kwargs))

    temporal_out_degree = lambda self, *args, **kwargs:\
        reduce(_reduce_sum, self.out_degree(*args, **kwargs))

    temporal_nodes = lambda self, *args, **kwargs:\
        (set if kwargs.get("data") is None else list)(v for V in self.nodes(*args, **kwargs) for v in V)

    temporal_edges = lambda self, *args, **kwargs:\
        (set if kwargs.get("data") is None else list)(e for E in self.edges(*args, **kwargs) for e in E)

    temporal_order = lambda self, *args, **kwargs:\
        len(set([n if kwargs.get("data") in (None, False) else (n[0], *n[1].keys(), *n[1].values())
        for n in self.temporal_nodes(*args, **kwargs)]))

    temporal_size = lambda self, *args, **kwargs:\
        len(set([e if kwargs.get("data") in (None, False) else (e[0], e[1], *e[2].keys(), *e[2].values())
        for e in self.temporal_edges(*args, **kwargs)]))

    total_order = lambda self: sum(self.order())
    total_size = lambda self: sum(self.size())


class TemporalGraph(TemporalBase):
    """
    Temporal graph with undirected edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=False, multigraph=False)


class TemporalDiGraph(TemporalBase):
    """
    Temporal graph with directed edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=True, multigraph=False)


class TemporalMultiGraph(TemporalBase):
    """
    Temporal multigraph with undirected edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=False, multigraph=True)


class TemporalMultiDiGraph(TemporalBase):
    """
    Temporal multigraph with directed edges.

    :param t: Number of snapshots to initialize (optional).
    """
    def __init__(self, t: Optional[int] = None) -> None:
        super().__init__(t=t, directed=True, multigraph=True)


def empty_graph(
    t: Optional[int] = None,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    create_using: Optional[Union[nx.Graph, TemporalGraph]] = None
) -> TemporalGraph:
    """
    Returns empty temporal graph of specified type.

    :param t: Number of snapshots to initialize.
    :param directed: If True, the graph will be directed.
    :param multigraph: If True, the graph will be a multigraph.
    :param create_using: Graph or temporal graph to use as reference.
    """
    assert create_using is None or (directed is None and multigraph is None),\
        "Arguments `directed` and `multigraph` are not allowed when `create_using` is passed."

    if create_using:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()

    if not directed and multigraph:
        return TemporalMultiGraph(t=t)

    elif directed and multigraph:
        return TemporalMultiDiGraph(t=t)

    elif not directed and not multigraph:
        return TemporalGraph(t=t)

    elif directed and not multigraph:
        return TemporalDiGraph(t=t)


def _reduce_sum(d1, d2):
    """ Returns sum of two integers or dictionaries. """
    if type(d1) == int or type(d2) == int:
        return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)

    d1, d2 = dict(d1), dict(d2)
    return {v: d1.get(v, 0) + d2.get(v, 0) for v in set(d for d in d1|d2)}
