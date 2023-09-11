from typing import Any, Callable, Literal, Optional, Union

import networkx as nx
import pandas as pd

from .networkx_temporal import (
    TemporalGraph,
    TemporalDiGraph,
    TemporalMultiGraph,
    TemporalMultiDiGraph
)


def empty_graph(
    t: Optional[int] = None,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    create_using: Optional[Union[nx.Graph, TemporalGraph]] = None
) -> TemporalGraph:
    """
    Returns empty temporal graph of specified type.

    :param directed: If True, the graph will be directed.
    :param multigraph: If True, the graph will be a multigraph.
    :param create_using: Graph or temporal graph to use as reference.
    """
    assert create_using is None or (directed is None and multigraph is None),\
        "Arguments `directed` and `multigraph` are not allowed when `create_using` is passed."

    if create_using:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()

    if not directed and not multigraph:
        return TemporalGraph(t=t)

    elif directed and not multigraph:
        return TemporalDiGraph(t=t)

    elif not directed and multigraph:
        return TemporalMultiGraph(t=t)

    elif directed and multigraph:
        return TemporalMultiDiGraph(t=t)


def from_events(events: list, directed: bool = False, multigraph: bool = False) -> list:
    """
    Returns temporal graph from sequence of events, i.e., (u, v, t) or (u, v, t, e).
    """
    assert events,\
        "Argument `events` must be a non-empty list."

    assert len(events[0]) in (3, 4),\
        f"Each event must have 3 or 4 elements, received: {len(events[0])}."

    TG = empty_graph(directed=directed,
                     multigraph=multigraph,
                     t=1 + max(events, key=lambda x: x[2])[2])

    if len(events[0]) == 3:
        list(TG[t].add_edge(u, v) for u, v, t in events)

    if len(events[0]) == 4:
        temporal_edges = {}
        for u, v, t, e in events:
            if e == 1:
                temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [t]
            if e == -1:
                for t_ in range(1 + temporal_edges[(u, v)][-1], t):
                    temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [t_]

        list(TG[t].add_edge(u, v) for (u, v), ts in temporal_edges.items() for t in ts)

    return TG


def from_snapshots(graphs: Union[dict, list]) -> list:
    """
    Returns temporal graph from sequence of snapshots.
    """
    T = list(graphs.keys() if type(graphs) == dict else range(len(graphs)))

    TG = empty_graph(create_using=graphs[T[0]])

    assert all(graphs[T[t]].is_directed() == TG.is_directed() for t in T),\
           "Mixed graphs and digraphs are not supported."

    assert all(graphs[T[t]].is_multigraph() == TG.is_multigraph() for t in T),\
           "Mixed graphs and multigraphs are not supported."

    TG._data = [graphs[T[t]] for t in T]
    return TG


def from_static(
    G: nx.Graph,
    attr: Optional[Union[str, list, dict]] = None,
    attr_level: Optional[Literal["node", "edge"]] = None,
    node_level: Optional[Literal["source", "target"]] = None,
    bins: Optional[int] = None,
    qcut: bool = False,
    duplicates: bool = False,
    rank_first: bool = False,
    apply_func: Optional[Callable[..., Any]] = None,
    fillna: Optional[Any] = None,
) -> dict:
    """
    Returns temporal graph from a static graph with node- or edge-level temporal data.

    Contrary to `nx.{edge_,}subgraph`, this method returns new graphs instead of a view,
    allowing for further manipulation without affecting the original graph object.

    Note that no data is lost when using this method, as it includes all nodes and
    edges from the original graph, plus additional features such as data binning.

    :param G: NetworkX graph.
    :param attr: Node- or edge-level attribute to consider as temporal data.
    :param attr_level: Level of temporal attribute, either 'node' or 'edge'.
    :param node_level: Level of temporal nodes to consider, either 'source' or 'target'.
    :param bins: Number of slices to create, must be a positive integer if set.
    :param qcut: If True, use quantiles to obtain time bins.
    :param duplicates: If False, raise an error when time bins contain duplicates.
    :param rank_first: If True, rank data points before slicing.
    :param apply_func: Function to apply to time attribute values.
    :param fillna: Value to fill null values in attribute data.
    """
    attr_level = attr_level.rstrip("s") if type(attr_level) == str else attr_level
    node_level = node_level.rstrip("s") if type(node_level) == str else node_level

    if attr is None:
        return from_snapshots([G])

    if attr_level == "node" and node_level is None:
        node_level = "source"

    assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `G` must be a valid NetworkX graph, received: {type(G)}."

    assert type(attr) in (str, list, dict, pd.Series, pd.DataFrame),\
        f"Argument `attr` accepts a str, list, dict, pandas series or data frame, received: {type(attr)}."

    assert type(attr) != str or attr_level in ("node", "edge"),\
        f"Argument `attr_level` must be either 'node' or 'edge', received: {type(attr)}."

    assert node_level in (None, "source", "target"),\
        f"Argument `node_level` must be either 'source' or 'target', received: {type(node_level)}."

    assert attr_level == "node" or node_level is None,\
        f"Argument `node_level` is not applicable to edge-level attribute data."

    assert not bins or bins > 0,\
        f"Argument `bins` must be a positive integer, received: {bins}."

    # Obtain temporal data from node-level or edge-level attribute.
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

    assert attr_level == "node" or len(times) == G.size(),\
        f"Length of `attr` differs from number of edges ({len(times)}, {G.size()})."

    assert attr_level == "edge" or len(times) == G.order(),\
        f"Length of `attr` differs from number of nodes ({len(times)}, {G.order()})."

    # Fill null values in attribute data.
    if times.isna().any():
        assert not times.isna().all(),\
            f"Attribute does not exist or contains null values only."
        assert fillna is not None,\
            f"Found null value(s) in attribute data, but `fillna` has not been set."
        times.fillna(fillna, inplace=True)

    edges = nx.to_pandas_edgelist(G)

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

        # Slice data in a given nuber of time bins.
        times = getattr(pd, "qcut" if qcut else "cut")(
            times,
            bins,
            duplicates="drop" if duplicates is False else "raise"
        )

        # Obtain edge temporal values from node-level data [1/1].
        if node_level:
            times = edges[node_level].apply(times.get)

    # Assign unique integer values to time bins.
    times = pd.Series(
        pd.factorize(times, sort=True)[0],
        index=times.index
    )

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
        for t, index in
            indices.items()
    ]

    # Add edges with attributes to created subgraphs.
    list(
        graphs[t].add_edges_from(
            edges
            .iloc[index]
            .apply(lambda e: (e["source"], e["target"], {k: v for k, v in e.items() if k not in ("source", "target")}), axis=1)
        )
        for t, index in
            indices.items()
    )

    return from_snapshots(graphs)


def from_unified(UTG: nx.Graph) -> list:
    """
    Returns temporal graph from unified temporal graph (UTG).

    Note that the UTG must be a valid unified temporal graph, i.e., it must contain
    temporal nodes in the format `node_timestamp`, where `node` is the original node
    name and `timestamp` is a non-negative integer.

    :param UTG: Unified temporal graph.
    """
    temporal_nodes = {}

    for node in UTG.nodes():
        t = node.rsplit("_", 1)[-1]
        assert t.isdigit(),\
                f"Unified temporal graph (UTG) contains non-temporal nodes ('{node}')."
        temporal_nodes[t] = temporal_nodes.get(t, []) + [node]

    return from_snapshots([
        nx.relabel_nodes(
            UTG.subgraph(temporal_nodes[t]),
            {v: v.rsplit("_", 1)[0] for v in temporal_nodes[t]}
        )
        for t in sorted(temporal_nodes.keys(), key=int)
    ])
