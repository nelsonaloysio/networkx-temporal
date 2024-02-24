from functools import reduce
from typing import Any, Callable, Literal, Optional, Union

import networkx as nx
import pandas as pd


class TemporalBase():
    """
    Base class for temporal graphs.

    :param directed: If True, the graph will be directed.
    :param multigraph: If True, the graph will be a multigraph.
    :param t: Number of time steps to initialize (optional).
    """
    def __init__(self, directed: bool = False, multigraph: bool = False, t: Optional[int] = None) -> None:
        """ Initializes a temporal graph. """
        assert t is None or type(t) == int,\
               f"Argument 't' must be an integer, received: `{type(t).__name__}`."

        assert t is None or t > 0,\
               f"Argument 't' must be greater than zero, received: {t}."

        self._directed = directed
        self._multigraph = multigraph
        self._data = [self.__empty_graph() for _ in range(t or 0)]

        for method in [_ for _ in dir(self.__empty_graph()) if not _.startswith("_")]:
            if method not in TemporalBase.__dict__:
                self.__setattr__(method, self.__wrapper(method))

    def __getitem__(self, t: int) -> nx.Graph:
        """ Returns temporal graph at a given time step. """
        assert self._data,\
               "Temporal graph is empty."
        assert type(t) in (int, slice),\
               f"Parameter must be an integer or slice, received: `{type(t).__name__}`."
        assert type(t) != int or -len(self) <= t < len(self),\
               f"Received index {t}, but temporal graph has t={len(self)} snapshots."
        assert type(t) != slice or -len(self) <= (t.start or 0) < (t.stop or len(self)) <= len(self),\
               f"Received slice {t.start, t.stop}, but temporal graph has t={len(self)} snapshots."
        return self._data[t]

    def __iter__(self) -> iter:
        """ Returns iterator over slices in the temporal graph. """
        return iter(self._data)

    def __len__(self) -> int:
        """ Returns number of slices in the temporal graph. """
        return len(self._data)

    def __new__(cls, *args, **kwargs) -> Any:
        """ Creates a new instance of the temporal graph. """
        if cls is TemporalBase:
            raise TypeError(f"{cls.__name__} cannot be instantiated.")
        new = super().__new__(cls)
        new.__init__(*args, **kwargs)
        return new

    def __repr__(self) -> str:
        """ Returns string representation of the temporal graph. """
        return f"{type(self).__name__}(t={len(self)})"

    @property
    def index(self) -> iter:
        """ Returns list of time indices in the temporal graph. """
        index = self.__dict__.get("_index")
        assert index is None or len(index) == len(self),\
                "Length of index does not match number of snapshots."
        return index or range(len(self))

    @property
    def t(self) -> int:
        """ Returns number of time steps in the temporal graph. """
        return len(self)

    def append(self, G: Optional[nx.Graph] = None) -> nx.Graph:
        """ Appends a new snapshot to the temporal graph. """
        self.insert(len(self), G)

    def insert(self, t, G: Optional[nx.Graph] = None) -> nx.Graph:
        """ Inserts a new snapshot at a given time step. """
        if G is None:
            G = self.__empty_graph()
        assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
                f"Argument 'G' must be a valid NetworkX graph, received: {type(G).__name__}."
        assert G.is_directed() == self.is_directed() and G.is_multigraph() == self.is_multigraph(),\
                f"Graph type ({type(G).__name__}) does not match temporal graph type ({type(self).__name})."
        self._data.insert(t, G)

    def pop(self, t: Optional[int] = None) -> nx.Graph:
        """ Removes and returns the snapshot at a given time step. """
        self.__getitem__(t or -1)
        return self._data.pop(t or -1)

    def slice(
        self,
        bins: Optional[int] = None,
        attr: Optional[Union[str, list, dict]] = None,
        attr_level: Optional[Literal["node", "edge"]] = None,
        node_level: Optional[Literal["source", "target"]] = None,
        qcut: bool = False,
        duplicates: bool = False,
        rank_first: bool = False,
        factorize: bool = False,
        fillna: Optional[Any] = None,
        apply_func: Optional[Callable[..., Any]] = None,
    ) -> list:
        """
        Slices temporal graph into time bins, returning a new temporal graph object.

        Contrary to `nx.{edge_,}subgraph`, this method returns new graphs instead of a view,
        allowing for further manipulation without affecting the original graph object.

        Note that no data is lost when using this method, as it includes all nodes and
        edges from the original graph, plus additional features such as data binning.

        :param bins: Number of slices to create.
        :param attr: Node- or edge-level attribute to consider as temporal data.
        :param attr_level: Level of temporal attribute, either 'node' or 'edge'.
        :param node_level: Level of temporal nodes to consider, either 'source' or 'target'.
        :param qcut: If True, use quantiles to obtain time bins.
        :param duplicates: If False, raise an error when time bins contain duplicates.
        :param rank_first: If True, rank data points before slicing.
        :param factorize: If True, assign unique integer values to time bins.
        :param fillna: Value to fill null values in attribute data.
        :param apply_func: Function to apply to time attribute values.
        """
        assert self._data,\
                "Temporal graph is empty."

        assert sum(self.order()),\
                "Temporal graph has no nodes."

        assert sum(self.size()),\
                "Temporal graph has no edges."

        # Set default values for optional arguments.
        rank_first = True if attr is None else rank_first
        node_level = "source" if attr_level == "node" and node_level is None else node_level

        # Check if attribute data is valid.
        assert attr is None or type(attr) in (str, list, dict, pd.Series, pd.DataFrame),\
               f"Argument `attr` accepts a str, list, dict, pandas Series or DataFrame, received: {type(attr).__name__}."

        assert type(attr) != str or attr_level in ("node", "edge"),\
               f"Argument `attr_level` must be either 'node' or 'edge' when `attr` is a string."

        assert node_level is None or attr_level == "node",\
               f"Argument `node_level` is not applicable to edge-level attribute data."

        assert node_level in ("source", "target") or attr_level != "node",\
               f"Argument `node_level` must be either 'source' or 'target' when slicing node-level attribute data."

        assert bins is None or bins > 0,\
               f"Argument `bins` must be a positive integer if set."

        # Obtain static graph object and edge data.
        G = self.to_static()
        edges = nx.to_pandas_edgelist(G)

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
            times = getattr(pd, "qcut" if qcut else "cut")(
                times,
                bins,
                duplicates="drop" if duplicates is False else "raise"
            )

            # Obtain edge temporal values from node-level data [1/1].
            if node_level:
                times = edges[node_level].apply(times.get)

        # Assign unique integer values to time bins.
        if factorize:
            times = pd.Series(
                pd.factorize(times, sort=True)[0],
                index=range(sum(self.size()))
            )
            times.map(lambda x: x.__str__())

        # Group edge indices by time.
        indices = edges.groupby(times).groups

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
        TG = self.__new__(self.__class__)
        TG._data = graphs
        TG._index = list(indices.keys())
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
        return self._data

    def to_static(self, attr_name: Optional[str] = None) -> nx.Graph:
        """
        Returns a static multigraph from a temporal graph.

        A static multigraph is a single object containing all nodes
        and edges of a temporal graph concatenated together.

        **Note**: this method does not preserve dynamic node attributes.

        :param attr_name: Edge attribute name to store time (optional).
        """
        assert attr_name not in next(iter(self[0].edges(data=True)))[2],\
                f"Edge attribute '{attr_name}' already exists in graph."

        G = nx.MultiDiGraph() if self.is_directed() else nx.MultiGraph()

        list(G.add_nodes_from(nodes)
             for nodes in self.nodes(data=True))

        list(G.add_edges_from([(e[0], e[1], e[2] if not attr_name else e[2]|{attr_name: t}) for e in edges])
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

    def __empty_graph(self) -> nx.Graph:
        """ Returns empty graph of the same type. """
        return getattr(nx, f"{'Multi' if self.is_multigraph() else ''}{'Di' if self.is_directed() else ''}Graph")()

    @staticmethod
    def __reduce_sum(d1, d2):
        """ Returns sum of two integers or dictionaries. """
        if type(d1) == int or type(d2) == int:
            return (d1 if type(d1) == int else 0) + (d2 if type(d2) == int else 0)
        return {v: dict(d1).get(v, 0) + dict(d2).get(v, 0) for v in set(d[0] for d in d1)|set(d[0] for d in d2)}

    def __wrapper(self, method) -> Callable:
        """ Returns a wrapper function for a given method. """
        def func(*args, **kwargs):
            if "t" in kwargs:
                return self.__getitem__(kwargs.pop("t")).__getattribute__(method)(*args, **kwargs)
            returns = list(G.__getattribute__(method)(*args, **kwargs) for G in self)
            return returns if any(r is not None for r in returns) else None
        return func

    is_directed = lambda self: self._directed
    is_multigraph = lambda self: self._multigraph

    neighbors = lambda self, v:\
        list(list(G.neighbors(v)) if G.has_node(v) else [] for G in self)

    temporal_neighbors = lambda self, v:\
        list(set(n for G in self if G.has_node(v) for N in G.neighbors(v) for n in N))

    temporal_degree = lambda self, *args, **kwargs:\
        reduce(self.__reduce_sum, self.degree(*args, **kwargs))

    temporal_in_degree = lambda self, *args, **kwargs:\
        reduce(self.__reduce_sum, self.in_degree(*args, **kwargs))

    temporal_out_degree = lambda self, *args, **kwargs:\
        reduce(self.__reduce_sum, self.in_degree(*args, **kwargs))

    temporal_nodes = lambda self, *args, **kwargs:\
        (set if kwargs.get("data") is None else list)(v for V in self.nodes(*args, **kwargs) for v in V)

    temporal_edges = lambda self, *args, **kwargs:\
        (set if kwargs.get("data") is None else list)(e for E in self.edges(*args, **kwargs) for e in E)

    temporal_order = lambda self, *args, **kwargs:\
        len(set([n if kwargs.get("data") is None else (n[0], *n[1].keys(), *n[1].values()) for n in self.temporal_nodes(*args, **kwargs)]))

    temporal_size = lambda self, *args, **kwargs:\
        len(set([e if kwargs.get("data") is None else (e[0], e[1], *e[2].keys(), *e[2].values()) for e in self.temporal_edges(*args, **kwargs)]))

    total_order = lambda self: sum(self.order())
    total_size = lambda self: sum(self.size())
