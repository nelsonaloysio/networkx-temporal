#!/usr/bin/env python

import logging as log
from argparse import ArgumentParser
from datetime import datetime
from os import remove

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

import networkx_temporal as tx

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def test_docs(*args, **kwargs) -> None:
    log.info("test_docs")
    gpu = kwargs.pop("test_gpu", False)
    pubmed = kwargs.pop("test_pubmed", False)

    test_basics()
    test_convert()
    test_metrics()
    test_community()
    test_gpu(gpu=gpu, pubmed=pubmed)

    print("All tests passed!")


def test_basics() -> None:
    """ docs/source/examples/basics.rst """
    log.info("test_basics")

    log.info("Build temporal graph")
    TG = tx.temporal_graph(directed=True)  # tx.TemporalMultiDiGraph()

    TG.add_edge("a", "b", time=0)
    TG.add_edge("c", "b", time=1)
    TG.add_edge("d", "c", time=2)
    TG.add_edge("d", "e", time=2)
    TG.add_edge("a", "c", time=2)
    TG.add_edge("f", "e", time=3)
    TG.add_edge("f", "a", time=3)
    TG.add_edge("f", "b", time=3)

    assert str(TG) == "TemporalMultiDiGraph (t=1) with 6 nodes and 8 edges"

    log.info("Import static graphs")
    G = nx.DiGraph()

    G.add_nodes_from([
        ("a", {"time": 0}),
        ("b", {"time": 0}),
        ("c", {"time": 1}),
        ("d", {"time": 2}),
        ("e", {"time": 3}),
        ("f", {"time": 3}),
    ])

    G.add_edges_from([
        ("a", "b", {"time": 0}),
        ("c", "b", {"time": 1}),
        ("d", "c", {"time": 2}),
        ("d", "e", {"time": 2}),
        ("a", "c", {"time": 2}),
        ("f", "e", {"time": 3}),
        ("f", "a", {"time": 3}),
        ("f", "b", {"time": 3}),
    ])

    TG = tx.from_static(G)
    assert str(TG) == "TemporalDiGraph (t=1) with 6 nodes and 8 edges"

    tx.draw(TG, layout="kamada_kawai",
            labels=True, edge_labels="time",
            suptitle="Temporal Graph")

    log.info("Slice temporal graph")
    TG = TG.slice(attr="time")  # level="edge" (default)
    assert str(TG) == "TemporalDiGraph (t=4) with 6 nodes and 8 edges"
    assert [(G.order(), G.size()) for G in TG] == [(2, 1), (2, 1), (4, 3), (4, 3)]

    tx.draw(TG, figsize=(8, 2), layout="kamada_kawai", labels=True)

    log.info("Define number of snapshots")
    TG = TG.slice(attr="time", bins=2)
    assert TG.index == ["(0, 1]", "(1, 3]"]
    tx.draw(TG, figsize=(4, 2), layout="kamada_kawai", labels=True, title=True)

    log.info("Cut by snapshot order or size")
    TG = TG.slice(3, attr="time", axis=1)
    assert TG.size() == [3, 3, 2]
    tx.draw(TG, figsize=(6, 2), layout="kamada_kawai", labels=True, title=False)

    TG = TG.slice(3, axis=1, level="node")
    assert TG.order() == [3, 3, 3, 3]
    tx.draw(TG, figsize=(8, 2), layout="kamada_kawai", labels=True, title=False)

    log.info("Node or edge attributes")
    TG = TG.slice(attr="time")
    assert TG.index == ["0", "1", "2", "3"]
    tx.draw(TG, figsize=(8, 2), layout="kamada_kawai", labels=True)

    TG_node = TG.slice(attr="time", level="node")
    assert TG_node.order() == [3, 2, 3, 4]
    tx.draw(TG_node, figsize=(8, 2), layout="kamada_kawai", labels=True)

    log.info("Quantile-based cut")
    TG = TG.slice(attr="time", bins=2, qcut=True)
    assert TG.index == ["(0, 2]", "(2, 3]"]
    tx.draw(TG, figsize=(4, 2), layout="kamada_kawai", labels=True, title=True)

    log.info("Rank-based cut")
    TG = TG.slice(bins=2, rank_first=True)
    assert TG.index == ["(0, 4]", "(4, 8]"]
    tx.draw(TG, figsize=(4, 2), layout="kamada_kawai", labels=True, title=True)

    log.info("Propagate snapshots")
    TG = tx.temporal_graph(directed=True)

    TG.add_edge("a", "b", time=0)
    TG.add_edge("c", "b", time=1)
    TG.add_edge("d", "c", time=2)
    TG.add_edge("d", "e", time=2)
    TG.add_edge("a", "c", time=2)
    TG.add_edge("f", "e", time=3)
    TG.add_edge("f", "a", time=3)
    TG.add_edge("f", "b", time=3)

    TG = TG.slice(attr="time")

    tx.draw(TG, figsize=(8,2), layout="kamada_kawai",
            labels=True, suptitle="Original Temporal Graph")

    TG_prop = tx.propagate_snapshots(TG, method="ffill")

    temporal_node_color = [
        ["green" if TG_prop.index_node(n)[0] == t else "tab:red"
         for n in G.nodes()] for t, G in enumerate(TG_prop)]

    temporal_edge_color = [
        ["tab:green" if TG_prop.index_edge((n1, n2))[0] == t else "black"
         for n1, n2 in G.edges()] for t, G in enumerate(TG_prop)]

    tx.draw(TG_prop, figsize=(8, 2), layout="kamada_kawai",
            labels=True, suptitle="Propagated Temporal Graph (ffill)",
            temporal_node_color=temporal_node_color,
            temporal_edge_color=temporal_edge_color)

    log.info("Save and load data")
    order, size = TG.order(), TG.size()
    tx.write_graph(TG, "temporal-graph.graphml.zip")
    TG = tx.read_graph("temporal-graph.graphml.zip")
    remove("temporal-graph.graphml.zip")
    assert TG.order() == order
    assert TG.size() == size

    log.info("Inherited methods")
    assert type(TG.to_undirected()) == tx.TemporalGraph
    assert type(TG.to_directed()) == tx.TemporalDiGraph

    log.info("Utility functions")
    TG = tx.temporal_graph(multigraph=False)

    TG.add_node("a", group=0)
    TG.add_node("b", group=1)
    TG.add_node("c", group=1)
    TG.add_node("d")

    TG.add_edge("a", "b", time=0)
    TG.add_edge("b", "c", time=0)
    TG.add_edge("a", "d", time=1)

    assert str(TG) == "TemporalGraph (t=1) with 4 nodes and 3 edges"

    log.info("Node and edge attributes")
    assert tx.get_node_attributes(TG, "group") == [{"a": 0, "b": 1, "c": 1}]
    assert tx.get_edge_attributes(TG, "time") == [{("a", "b"): 0, ("a", "d"): 1, ("b", "c"): 0}]

    log.info("Partition node and edge sets")
    assert tx.partition_nodes(TG, "group", default="unknown") ==\
        [{0: {"a"}, 1: {"b", "c"}, "unknown": {"d"}}]
    # Node order within each partition is not guaranteed (set-based).
    assert [[set(p) for p in P] for P in tx.partition_nodes(TG, "group", index=False)] ==\
        [[{"a"}, {"b", "c"}]]
    assert tx.partition_edges(TG, "time") == [{0: [("a", "b"), ("b", "c")], 1: [("a", "d")]}]

    log.info("Mapping node and edge attributes")
    assert tx.map_edge_attr_to_nodes(TG, "time", unique=True) ==\
        [{"a": [0, 1], "b": [0], "c": [0], "d": [1]}]
    assert tx.map_node_attr_to_edges(TG, "group", origin="source") ==\
        [{("a", "b"): 0, ("a", "d"): 0, ("b", "c"): 1}]

    log.info("Similarity of node and edge sets")
    snapshots = TG.slice(attr="time")
    assert tx.temporal_node_similarity(snapshots, method="jaccard") == [[1.0, 0.25], [0.25, 1.0]]

    plt.close("all")


def test_convert() -> None:
    """ docs/source/examples/convert.rst """
    log.info("test_convert")

    log.info("Graph types and classes")
    TG = tx.temporal_graph(directed=True)  # tx.TemporalMultiDiGraph()

    TG.add_edge("a", "b", time=0)
    TG.add_edge("c", "b", time=1)
    TG.add_edge("d", "c", time=2)
    TG.add_edge("d", "e", time=2)
    TG.add_edge("a", "c", time=2)
    TG.add_edge("f", "e", time=3)
    TG.add_edge("f", "a", time=3)
    TG.add_edge("f", "b", time=3)

    assert str(TG) == "TemporalMultiDiGraph (t=1) with 6 nodes and 8 edges"

    TG.add_edge("c", "b", time=0)   # <-- parallel edge
    assert str(TG) == "TemporalMultiDiGraph (t=1) with 6 nodes and 9 edges"

    TG = tx.from_multigraph(TG)
    assert TG.edge("c", "b") == {0: {"time": 0, "weight": 2}}

    TG = tx.to_multigraph(TG)
    assert str(TG) == "TemporalMultiDiGraph (t=1) with 6 nodes and 8 edges"

    TG.add_edge("c", "b", time=1)   # <-- parallel edge
    assert str(TG) == "TemporalMultiDiGraph (t=1) with 6 nodes and 9 edges"

    log.info("Static graph: TG -> G")
    G = TG.to_static()
    assert str(G) == "MultiDiGraph with 6 nodes and 9 edges"

    tx.draw(G, layout="kamada_kawai", labels=True, suptitle="Static Graph")

    log.info("Static graph: G -> TG")
    TG = tx.from_static(G)
    TG = TG.slice(attr="time")
    assert str(TG) == "TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges"

    log.info("Snapshot-based temporal graph: TG -> STG")
    STG = TG.to_snapshots()
    assert len(STG) == 4
    assert all(type(G) == nx.MultiDiGraph for G in STG)

    log.info("Snapshot-based temporal graph: STG -> TG")
    TG = tx.from_snapshots(STG).copy()
    assert str(TG) == "TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges"

    log.info("Event-based temporal graph: TG -> ETG")
    ETG = TG.to_events()  # delta=None
    assert ETG == [
        ("a", "b", 0),
        ("c", "b", 0),
        ("c", "b", 1),
        ("a", "c", 2),
        ("d", "c", 2),
        ("d", "e", 2),
        ("f", "e", 3),
        ("f", "a", 3),
        ("f", "b", 3),
    ]

    ETG = TG.to_events(delta=int)
    assert ETG == [
        ("a", "b", 0, 1),
        ("c", "b", 0, 1),
        ("a", "b", 1, -1),
        ("a", "c", 2, 1),
        ("d", "c", 2, 1),
        ("d", "e", 2, 1),
        ("c", "b", 2, -1),
        ("f", "e", 3, 1),
        ("f", "a", 3, 1),
        ("f", "b", 3, 1),
        ("a", "c", 3, -1),
        ("d", "c", 3, -1),
        ("d", "e", 3, -1),
    ]

    ETG = TG.to_events(delta=float)
    assert ETG == [
        ("a", "b", 0, 0.0),
        ("c", "b", 0, 1.0),
        ("a", "c", 2, 0.0),
        ("d", "c", 2, 0.0),
        ("d", "e", 2, 0.0),
        ("f", "e", 3, 0.0),
        ("f", "a", 3, 0.0),
        ("f", "b", 3, 0.0),
    ]

    log.info("Event-based temporal graph: ETG -> TG")
    TG = tx.from_events(ETG, directed=True, multigraph=True)
    assert str(TG) == "TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges"

    log.info("Unrolled temporal graph: TG -> UTG")
    UTG = TG.to_unrolled(edge_couplings=True)
    assert str(UTG) == "MultiDiGraph named 'UnrolledTemporalGraph' with 13 nodes and 16 edges"

    def draw_unrolled(UTG, **kwargs):
        return tx.draw(
            UTG,
            layout=tx.unrolled_layout,
            labels={n: f"{n.split('_')[0]}$_{n.split('_')[1]}$" for n in UTG.nodes()},
            style=[':' if u.split("_", 1)[0] == v.split("_", 1)[0] else '-' for u, v in UTG.edges()],
            font_size=10,
            arrowsize=15,
            **kwargs,
        )

    node_color = [
        "tab:red" if int(n.split("_")[1]) == TG.index_node(n.split("_")[0])[0] else "#333"
        for n in UTG.nodes()]

    draw_unrolled(UTG,
                  node_color=node_color,
                  connectionstyle="arc3,rad=0.25",
                  title="Unrolled Temporal Graph")

    UTG_delta = TG.to_unrolled(delta=1)

    node_color = [
        "#333" if UTG.has_node(n) else "tab:green" for n in UTG_delta.nodes()]

    draw_unrolled(UTG_delta,
                  node_color=node_color,
                  connectionstyle="arc3,rad=0.1",
                  title="Unrolled Temporal Graph ($\\delta=1$)")

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(8, 2))

    UTG_fill = TG.to_unrolled(delta=1, node_copies="fill")
    UTG_persist = TG.to_unrolled(delta=1, node_copies="persist")
    UTG_all = TG.to_unrolled(delta=1, node_copies="all")

    draw_unrolled(
        UTG_fill,
        node_color=["#333" if UTG.has_node(n) else "tab:green" for n in UTG_fill.nodes()],
        node_size=200, fig=fig, ax=0, title="node_copies='fill'")

    draw_unrolled(
        UTG_persist,
        node_color=["#333" if UTG_fill.has_node(n) else "tab:green" for n in UTG_persist.nodes()],
        node_size=200, fig=fig, ax=1, title="node_copies='persist'")

    draw_unrolled(
        UTG_all,
        node_color=["#333" if UTG_persist.has_node(n) else "tab:green" for n in UTG_all.nodes()],
        node_size=200, fig=fig, ax=2, title="node_copies='all'")

    log.info("Unrolled temporal graph: UTG -> TG")
    TG = tx.from_unrolled(UTG)
    assert str(TG) == "TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges"

    log.info("External library formats")
    graphs = tx.convert(TG, "igraph")
    assert len(graphs) == len(TG)
    assert all(type(g).__module__.startswith("igraph") for g in graphs)

    g = tx.convert(TG.to_static(), "igraph")
    assert type(g).__module__.startswith("igraph")

    log.info("File readers and writers")
    tx.write_graph(TG, "temporal-graph.graphml.zip")
    TG = tx.read_graph("temporal-graph.graphml.zip")
    remove("temporal-graph.graphml.zip")
    assert str(TG) == "TemporalDiGraph (t=4) with 6 nodes and 9 edges"

    byte_data = tx.write_graph(TG, format="graphml")
    TG = tx.read_graph(byte_data)
    assert str(TG) == "TemporalDiGraph (t=4) with 6 nodes and 9 edges"

    plt.close("all")


def test_metrics() -> None:
    """ docs/source/examples/metrics.rst """
    log.info("test_metrics")

    log.info("Graph properties")
    TG = tx.temporal_graph(directed=True)  # tx.TemporalMultiDiGraph()

    TG.add_edge("a", "b", time=0)
    TG.add_edge("c", "b", time=0)
    TG.add_edge("c", "b", time=1)   # <- parallel edge
    TG.add_edge("d", "c", time=2)
    TG.add_edge("d", "e", time=2)
    TG.add_edge("a", "c", time=2)
    TG.add_edge("f", "e", time=3)
    TG.add_edge("f", "a", time=3)
    TG.add_edge("f", "b", time=3)

    TG = TG.slice(attr="time")
    assert str(TG) == "TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges"

    assert TG.order() == [3, 2, 4, 4]
    assert TG.order(copies=False) == 6
    assert TG.order(copies=True) == 13

    assert TG.size() == [2, 1, 3, 3]
    assert TG.size(copies=False) == 8
    assert TG.size(copies=True) == 9

    tx.draw(TG, figsize=(8,2), layout="kamada_kawai", labels=True)

    log.info("Node neighborhoods: per snapshot")
    TG = TG.slice(attr="time")
    # Node order is not guaranteed (set-based).
    assert [set(n) for n in TG.neighbors("c")] == [{"b"}, {"b"}, set(), set()]
    assert [set(n) for n in TG.to_undirected().neighbors("c")] == [{"b"}, {"b"}, {"a", "d"}, set()]

    log.info("Node neighborhoods: from all snapshots")
    assert set(tx.neighbors(TG, "c")) == {"b"}
    assert set(tx.neighbors(TG.to_undirected(), "c")) == {"b", "a", "d"}
    assert set(tx.neighbors(TG[0:2], "c")) == {"b"}

    log.info("Node centrality")
    katz_t = []
    for t, G in enumerate(TG):
        # We convert the multigraph to a simple graph first,
        # as Katz centrality is not implemented for multigraphs.
        G = tx.from_multigraph(G)
        katz = nx.katz_centrality(G)
        katz = {node: round(value, 2) for node, value in katz.items()}
        katz_t.append(katz)

    assert katz_t == [
        {"a": 0.54, "b": 0.65, "c": 0.54},
        {"b": 0.74, "c": 0.67},
        {"a": 0.46, "c": 0.56, "d": 0.46, "e": 0.51},
        {"a": 0.51, "b": 0.51, "e": 0.51, "f": 0.46},
    ]

    log.info("Node degrees")
    assert [dict(d) for d in TG.degree()] == [
        {"a": 1, "b": 2, "c": 1},
        {"b": 1, "c": 1},
        {"a": 1, "c": 2, "d": 2, "e": 1},
        {"a": 1, "b": 1, "e": 1, "f": 3},
    ]
    assert TG.degree("a") == [1, None, 1, 1]

    log.info("Degree centrality")
    assert tx.degree(TG) == {"a": 3, "b": 4, "c": 4, "d": 2, "e": 2, "f": 3}
    assert tx.degree(TG, "a") == 3
    assert tx.degree_centrality(TG) == {"a": 0.6, "b": 0.8, "c": 0.8, "d": 0.4, "e": 0.4, "f": 0.6}
    assert tx.degree_centrality(TG, "a") == 0.6

    log.info("Graph centralization")
    G = nx.star_graph(10)
    tx.draw(G, layout="fruchterman_reingold")

    log.info("Degree centralization")
    assert tx.degree_centralization(TG) == [1.0, 0.0, 0.3333333333333333, 1.0]
    assert tx.in_degree_centralization(TG) != tx.out_degree_centralization(TG)

    dc = []
    for t, G in enumerate(TG):
        indc = tx.in_degree_centralization(G)
        outdc = tx.out_degree_centralization(G)
        dc.append(f"t={t}: in={indc:.2f}, out={outdc:.2f}")

    assert dc == [
        "t=0: in=1.00, out=0.25",
        "t=1: in=1.00, out=1.00",
        "t=2: in=0.56, out=0.56",
        "t=3: in=0.11, out=1.00",
    ]

    G = nx.star_graph(10)  # Rebuild star graph.
    G.add_node(-1)         # Disconnected node.
    G.add_edge(0, 0)       # Edge self-loop.

    assert tx.degree_centralization(G) == 1.0
    assert f"{tx.degree_centralization(G, isolates=True):.3f}" == "0.909"
    assert f"{tx.degree_centralization(G, self_loops=True):.3f}" == "1.222"
    assert f"{tx.degree_centralization(G, isolates=True, self_loops=True):.3f}" == "1.109"

    log.info("Centralization metrics")
    G = nx.star_graph(10)
    centrality = G.degree()
    scalar = sum(G.order() - 2 for n in range(G.order()-1))  # |V|-1 for DiGraph

    centralization = tx.centralization(centrality=centrality, scalar=scalar)
    assert f"{centralization:.2f}" == "1.00"

    log.info("Temporal dynamics")
    TG = tx.collegemsg_graph()
    assert str(TG) == "TemporalMultiDiGraph named 'CollegeMsg' (t=193) with 1899 nodes and 59835 edges"
    assert (TG.index[0], TG.index[-1]) == ("2004-04-15", "2004-10-26")

    def strftime(x, fmt="%Y, Week %W"):
       # Convert date to weekly intervals with ascending sorting.
       return datetime.strptime(x, "%Y-%m-%d %H:%M").strftime(fmt)

    TG = tx.collegemsg_graph()
    TG = TG.slice(attr="time", applymap=strftime)
    assert str(TG) == "TemporalMultiDiGraph named 'CollegeMsg' (t=29) with 1899 nodes and 59835 edges"
    assert (TG.index[0], TG.index[-1]) == ("2004, Week 15", "2004, Week 43")

    t_max_order = TG.order().index(max(TG.order()))
    t_max_size = TG.size().index(max(TG.size()))

    assert (t_max_order, TG.index[t_max_order], TG[t_max_order].order()) ==\
        (6, "2004, Week 21", 904)
    assert (t_max_size, TG.index[t_max_size], TG[t_max_size].size()) ==\
        (3, "2004, Week 18", 10194)

    log.info("Degree distribution")
    G = TG.to_static()

    fig, ax = plt.subplot_mosaic([["Left", "TopRight"],["Left", "BottomRight"]],
                                  constrained_layout=True, figsize=(8, 4), sharex=True,
                                  gridspec_kw={"width_ratios": [3, 1]})

    def deg_plot(df, ax, color="#555", title=None, xlabel=None, ylabel=None):
       # Plot degree distribution as a line plot with log-scaled x-axis.
       df[df > 0].value_counts().sort_index().plot.line(
          ax=ax, color=color, logx=True, marker="x", markersize=3, linewidth=.9)
       ax.grid(color="#ccc", linestyle=":", linewidth=1, alpha=1.0, which="major")
       ax.grid(color="#ccc", linestyle=":", linewidth=1, alpha=0.5, which="minor")
       ax.set_title(title, fontsize=10)
       ax.set_xlabel(xlabel)
       ax.set_ylabel(ylabel)

    def hist_plot(df, bins, ax, title="", xlabel="", ylabel="", color="#555"):
       # Plot histogram of degree distribution with log-scaled y-axis.
       hist = pd.cut(df[df > 0], bins=bins, right=False)
       hist.value_counts().sort_index().plot.bar(ax=ax, logy=True, color=color, width=0.7)
       ax.grid(color="#ccc", linestyle=":", linewidth=1, alpha=1.0, which="major", axis="y")
       ax.tick_params(axis='both', which="major", labelsize=9)
       ax.set_title(title, fontsize=9)
       ax.set_xlabel(xlabel, fontsize=9)
       ax.set_xticklabels([f"<{b}" for b in bins[1:]])
       ax.set_ylabel(ylabel, fontsize=9)
       ax.set_yticks([], minor=True)
       ax.set_yticks([1, 10, 100, 1000])

    deg = pd.Series(dict(G.degree()))
    deg_in = pd.Series(dict(G.in_degree()))
    deg_out = pd.Series(dict(G.out_degree()))

    deg_plot(deg, ax["Left"], xlabel="Degree (log-scaled)", ylabel="Frequency")
    deg_plot(deg_in, ax["TopRight"], title="In-Degree (log)", color="#333")
    deg_plot(deg_out, ax["BottomRight"], xlabel="Out-Degree (log)", color="#777")

    bins = [0, 10, 100, 1000, 10000]

    hist_plot(deg, bins, ax["Left"].inset_axes([0.67, 0.59, 0.3, 0.32]),
             title="Degree Histogram", xlabel="Degree", ylabel="Frequency (log)")
    hist_plot(deg_in, bins, ax["TopRight"].inset_axes([0.5, 0.48, 0.45, 0.45]), color="#333")
    hist_plot(deg_out, bins, ax["BottomRight"].inset_axes([0.5, 0.48, 0.45, 0.45]), color="#777")

    # Share y-axis between top-right and bottom-right insets.
    ax["BottomRight"].sharey(ax["TopRight"])
    ax["TopRight"].autoscale(axis="y")

    plt.suptitle("Node Degree Distributions on Static Graph", fontsize=11, y=1, fontweight="bold")

    log.info("General statistics")
    df = pd.DataFrame({
       "nodes": TG.order(),
       "edges": TG.size(),
       "deg_mean": [sum(d[1] for d in deg)/len(deg) for deg in TG.degree()],
       # "deg_in_min": [min(d[1] for d in deg) for deg in TG.in_degree()],
       # "deg_out_min": [min(d[1] for d in deg) for deg in TG.out_degree()],
       "deg_in_max": [max(d[1] for d in deg) for deg in TG.in_degree()],
       "deg_out_max": [max(d[1] for d in deg) for deg in TG.out_degree()],
       "cent_in": tx.in_degree_centralization(TG),
       "cent_out": tx.out_degree_centralization(TG)},
       index=TG.index)

    assert df.describe().iloc[1:].round(2).to_dict(orient="list") == {
        "nodes": [311.45, 258.45, 4.0, 145.0, 197.0, 342.0, 904.0],
        "edges": [2063.28, 3071.82, 2.0, 385.0, 648.0, 1431.0, 10194.0],
        "deg_mean": [8.66, 6.68, 1.0, 5.08, 6.13, 8.4, 25.74],
        "deg_in_max": [67.62, 55.98, 1.0, 28.0, 45.0, 94.0, 192.0],
        "deg_out_max": [105.38, 100.95, 1.0, 37.0, 87.0, 137.0, 493.0],
        "cent_in": [0.06, 0.04, 0.02, 0.04, 0.06, 0.08, 0.22],
        "cent_out": [0.15, 0.08, 0.05, 0.09, 0.14, 0.18, 0.43],
    }

    log.info("Temporal activity")
    # Include date in x-axis labels for better readability.
    def to_date(x):
        if not x.get_text():
            return ""
        return datetime.strptime(f"{x.get_text()} 0", "%Y, Week %W %w")\
                       .strftime("Week %W\n(%b %d, %Y)")

    fig, axs = plt.subplots(figsize=(6, 6), nrows=3, ncols=1,
                            constrained_layout=True, sharex=True)

    plt.suptitle("CollegeMsg graph (%s weeks, %s nodes, %s edges)" %
                 (len(TG), TG.order(copies=False), TG.size(copies=True)))

    df[["nodes", "edges"]].plot(ax=axs[0], color=["#1f77b4cc", "#ff7f0ecc"])
    df[["deg_in_max", "deg_out_max"]].plot(ax=axs[1], color=["#2ca02ccc", "#d62728cc"])
    df[["cent_in", "cent_out"]].plot(ax=axs[2], color=["#8e508ecc", "#c8c107cc"])

    axs[0].legend(labels=["Total nodes", "Total edges"])
    axs[1].legend(labels=["Max. node in-degree", "Max. node out-degree"])
    axs[2].legend(labels=["In-degree centralization", "Out-degree centralization"])

    for i, ax in enumerate(axs):
        ax.set_xlim((0, df.shape[0]-1))
        ax.set_ylim((0, ax.get_ylim()[1]))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.grid(color="#ccc", linestyle=":", linewidth=1, alpha=1.0, which='major')
        ax.grid(color="#ccc", linestyle=":", linewidth=1, alpha=0.5, which='minor')

    ax.set_xticklabels([to_date(x) for x in ax.get_xticklabels()], rotation=10)

    log.info("Temporal evolution")
    def plot_heatmap(data, ax, title, cmap="turbo", vmin=0, vmax=1):
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.spines[:].set_visible(False)
        ax.set_title(title)
        ax.set_xticks(range(0, len(TG), 4))
        ax.set_yticks(range(0, len(TG), 4))
        ax.set_xticks([i-0.5 for i in range(len(TG))], minor=True)
        ax.set_yticks([i-0.5 for i in range(len(TG))], minor=True)
        ax.set_xticklabels([TG.index[i] for i in ax.get_xticks()], rotation=90)
        ax.set_yticklabels([TG.index[i] for i in ax.get_yticks()])
        ax.tick_params(which="minor", bottom=False, left=False)
        ax.grid(which="minor", color="w", linestyle='dotted', linewidth=0.5)
        x0, y0, x1, y1 = ax.get_position().bounds
        cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.set_position([x1 + 0.01, y0, 0.02, y1 - y0])
        return cbar

    fig, axs = plt.subplots(figsize=(8, 4), ncols=2)

    intersect = tx.temporal_node_similarity(TG, method="intersect")
    dice = tx.temporal_node_similarity(TG, method="dice")

    plot_heatmap(intersect, axs[0], "Node set intersection")
    plot_heatmap(dice, axs[1], "Node set similarity (Dice)")

    plt.subplots_adjust(wspace=0.8)

    fig, axs = plt.subplots(figsize=(8, 4), ncols=2)

    intersect = tx.temporal_edge_similarity(TG.to_undirected(), method="intersect")
    dice = tx.temporal_edge_similarity(TG.to_undirected(), method="dice")

    plot_heatmap(intersect, axs[0], "Edge set intersection")
    plot_heatmap(dice, axs[1], "Edge set similarity (Dice)")

    plt.subplots_adjust(wspace=0.8)

    plt.close("all")


def test_community() -> None:
    """ docs/source/examples/community.rst """
    log.info("test_community")

    log.info("Generate graph")
    TG = tx.TemporalGraph()

    for r in [0, .125, .25, .375]:
        p = tx.generate_block_matrix(k=5, p=.9-r, q=.1+r)
        G = nx.stochastic_block_model(p=p, sizes=[5]*5, seed=10)
        TG.add_snapshot(G)

    assert str(TG) == "TemporalGraph (t=4) with 25 nodes and 426 edges"

    colors = plt.cm.tab10.colors

    def get_edge_color(edges, node_color):
        edge_color = []
        for u, v in edges:
            if node_color[u] == node_color[v]:
                edge_color.append(node_color[u])  # Within-community edge.
            else:
                edge_color.append((0, 0, 0, .25))  # Inter-community edge.
        return edge_color

    # Node positions.
    pos = nx.circular_layout(TG.to_static())

    # Node options for all graphs; colorize nodes by block/community.
    node_color = [colors[x % len(colors)] for n, x in TG[0].nodes(data="block")]

    # Plot snapshots with community ground truths.
    tx.draw(TG, pos=pos, labels=True,
            figsize=(12, 3.5), node_size=300,
            node_color=node_color, edge_color=(0, 0, 0, .3),
            suptitle="Ground truths")

    log.info("Optimizing static modularity")
    G = TG.to_static()
    assignments = tx.leiden_communities(G, max_iter=-1, seed=0)

    node_color = [colors[x % len(colors)] for x in assignments]

    tx.draw(G, pos=pos, labels=True,
            figsize=(4,4), node_size=300,
            node_color=node_color, edge_color=get_edge_color(G.edges(), node_color),
            connectionstyle="arc3,rad=0.1",
            suptitle="Modularity optimization on static graph")

    snapshot_assignments = [
        tx.leiden_communities(G, max_iter=-1, seed=0) for G in TG
    ]

    temporal_node_color = [
        [colors[m] for m in snapshot_assignments[t]]
        for t in range(len(TG))
    ]

    tx.draw(TG, pos=pos, labels=True,
            figsize=(12, 3.5), node_size=300,
            temporal_node_color=temporal_node_color,
            temporal_edge_color=[
                 get_edge_color(G.edges(), temporal_node_color[t])
                 for t, G in enumerate(TG)
             ],
             connectionstyle="arc3,rad=0.1",
             suptitle="Modularity optimization on graph snapshots")

    log.info("Optimizing multislice modularity")
    multislice_assignments = tx.leiden_communities(TG, max_iter=-1, seed=0)

    temporal_node_color = [
        [colors[m] for m in multislice_assignments[t]]
        for t in range(len(TG))
    ]

    tx.draw(TG, pos=pos, labels=True,
            figsize=(12, 3.5), node_size=300,
            temporal_node_color=temporal_node_color,
            temporal_edge_color=[
                get_edge_color(G.edges(), temporal_node_color[t])
                for t, G in enumerate(TG)
            ],
            connectionstyle="arc3,rad=0.1",
            suptitle="Modularity optimization on multislice graph")

    log.info("Evaluating community structures")
    optimization = ("Static", "Snapshot", "Multislice")
    static_assignments = dict(enumerate(assignments))
    partitions = (static_assignments, snapshot_assignments, multislice_assignments)

    results = {}
    for m, labels in zip(optimization, partitions):
       Q = tx.modularity(TG, labels)
       mean = sum(Q) / len(Q)
       Q = [round(q, 3) for q in Q]
       results[m] = (Q, f"{mean:.3f}")

    assert results == {
        "Static": ([0.057, 0.099, 0.058, 0.026], "0.060"),
        "Snapshot": ([0.468, 0.26, 0.194, 0.147], "0.267"),
        "Multislice": ([0.468, 0.21, 0.122, -0.005], "0.199"),
    }

    results = {}
    for m, labels in zip(optimization, partitions):
       conductance = tx.conductance(TG, labels)
       mean = sum(conductance) / len(conductance)
       conductance = [round(c, 3) for c in conductance]
       results[m] = (conductance, f"{mean:.3f}")

    assert results == {
        "Static": ([0.449, 0.419, 0.464, 0.493], "0.456"),
        "Snapshot": ([0.323, 0.487, 0.463, 0.371], "0.411"),
        "Multislice": ([0.323, 0.589, 0.68, 0.808], "0.600"),
    }

    log.info("Time-aware quality functions")
    Q_ms = tx.modularity_multislice(TG, multislice_assignments, interslice_weight=1)
    assert f"{Q_ms:.3f}" == "0.205"

    log.info("Mixed-membership communities")
    TG = tx.TemporalGraph()
    TG.add_edges_from([
        ("a", "b"), ("b", "c"), ('c', "a"), ("d", "a"),
        ("e", "f"), ("f", "g"), ("g", "e"), ("d", "e"),
    ])
    tx.draw(TG, labels=True, layout="spring", node_color=list("rrr0ggg"))

    G = TG.to_static()
    community_vector = [0, 0, 0,  1 , 2, 2, 2]
    assert tx.modularity(G, community_vector) == 0.3515625

    community_vector = [0, 0, 0,  0 , 1, 1, 1]
    assert tx.modularity(G, community_vector) == 0.3671875

    community_matrix = tx.community_matrix_from_vector(community_vector)
    community_matrix[3] = [0.5, 0.5]  # Node 'd' in both communities with equal weights.
    assert community_matrix.tolist() == [
        [1.0, 0.0],
        [1.0, 0.0],
        [1.0, 0.0],
        [0.5, 0.5],
        [0.0, 1.0],
        [0.0, 1.0],
        [0.0, 1.0],
    ]

    assert tx.modularity(G, community_matrix, spectral=True) == 0.375

    plt.close("all")


def test_gpu(gpu: bool = False, pubmed: bool = False) -> None:
    """ docs/source/examples/gpu.rst

    :param gpu: Run examples with ``device='gpu'`` (requires CuPy/cuGraph).
    :param pubmed: Run examples on the PubMed dataset (CPU multislice Leiden takes ~1 minute).
    """
    log.info("test_gpu")

    log.info("Accelerating temporal graph algorithms")
    log.info("is_gpu_enabled: %s", tx.is_gpu_enabled)

    log.info("Community detection")
    TG = tx.example_sbm_graph()
    assert str(TG) == "TemporalMultiGraph (t=3) with 75 nodes and 589 edges"

    log.info("Spectral clustering")
    y_pred = tx.spectral_clustering(TG, k=3)  # operator="laplacian" (default)
    assert [len(y) for y in y_pred] == TG.order()

    colors = plt.cm.tab10.colors

    def plot_temporal_graph(TG, y_pred):
        y_true = tx.get_node_attributes(TG, "community", index=False)
        pos = tx.layout(TG, layout="kamada_kawai")
        temporal_node_color = [
            [colors[m % len(colors)] for m in s]
            for y in [y_true, y_pred]
            for s in y
        ]
        # Draw ground truths (top) and clustering results (bottom).
        return tx.draw(
            [*TG, *TG], figsize=(6, 3.5), nrows=2, ncols=3,
            pos=[*pos, *pos], node_size=50, title=False,
            suptitle=f"Ground Truths (top) vs. Clustering Results (bottom)",
            temporal_node_color=temporal_node_color)

    plot_temporal_graph(TG, y_pred)

    G = TG.to_static()
    y_pred = tx.spectral_clustering(G, k=3)
    assert len(y_pred) == G.order()

    def plot_static_graph(G, y_pred):
        y_true = tx.get_node_attributes(G, "community", index=False)
        pos = tx.layout(G, layout="kamada_kawai")
        node_color = [
            [colors[m % len(colors)] for m in y]
            for y in [y_true, y_pred]
        ]
        # Draw ground truths (left) and clustering results (right).
        return tx.draw(
            [G, G], figsize=(6, 3), pos=pos, node_size=70,
            title=["Ground Truths", "Clustering Results"],
            temporal_node_color=node_color)

    plot_static_graph(G, y_pred)

    log.info("Leiden communities")
    y_pred = tx.leiden_communities(TG)
    assert [len(y) for y in y_pred] == TG.order()

    plot_temporal_graph(TG, y_pred)

    if pubmed:
        log.info("Temporal multislice optimization")
        TG = tx.pubmed_graph()
        assert str(TG) == "TemporalDiGraph named 'PubMed' (t=42) with 19717 nodes and 44335 edges"

        y = tx.leiden_communities(TG, max_iter=2, device="cpu")
        assert [len(s) for s in y] == TG.order()

        if gpu:
            y = tx.leiden_communities(TG, max_iter=2, device="gpu")
            assert [len(s) for s in y] == TG.order()
            y = tx.leiden_communities(TG, max_iter=2, device="gpu", refine=False)
            assert [len(s) for s in y] == TG.order()

        log.info("Static modularity optimization")
        G = TG.to_static()
        assert str(G) == "DiGraph named 'PubMed' with 19717 nodes and 44335 edges"

        y = tx.leiden_communities(G, max_iter=2, device="cpu")
        assert len(y) == G.order()

        if gpu:
            y = tx.leiden_communities(G, max_iter=2, device="gpu")
            assert len(y) == G.order()

        log.info("Static supra-graph optimization")
        adj = tx.to_supra_adjacency_matrix(TG)
        G_supra = tx.from_scipy(adj)
        # Size is not asserted: the directed supra-adjacency matrix is read as undirected, keeping
        # only upper-triangle entries, which depend on the (hash-seeded) node order of snapshots.
        assert G_supra.order() == 37003

        if gpu:
            y = tx.leiden_communities(G_supra, max_iter=2, device="gpu")
            assert len(y) == G_supra.order()

    log.info("Compare detection accuracy")
    max_iter = 100

    # Multislice modularity optimization.
    TG = tx.example_sbm_graph()
    y_cpu_TG = tx.leiden_communities(TG, device="cpu", max_iter=max_iter)
    if gpu:
        y_gpu_TG = tx.leiden_communities(TG, device="gpu", max_iter=max_iter)
        y_gpu_TG_norefine = tx.leiden_communities(TG, device="gpu", max_iter=max_iter,
                                                  refine=False)

    # Static modularity optimization.
    G = TG.to_static()
    y_cpu_G = tx.leiden_communities(G, device="cpu", max_iter=max_iter)
    if gpu:
        y_gpu_G = tx.leiden_communities(G, device="gpu", max_iter=max_iter)

    # Build supra-graph connecting nodes across time slices (default interslice_weight=1.0).
    adj, offsets = tx.to_supra_adjacency_matrix(TG, return_offsets=True)
    G_supra = tx.from_scipy(adj)

    # Supra-graph (static) modularity optimization.
    if gpu:
        y_gpu_G_supra = tx.leiden_communities(G_supra, device="gpu", max_iter=max_iter)
        y_gpu_G_supra = [y_gpu_G_supra[offsets[t]:offsets[t] + len(TG[t])]
                         for t in range(len(TG))]

    log.info("Static graph optimization")
    y_true_G = tx.get_node_attributes(G, "community", index=False)
    pos = tx.layout(G, layout="kamada_kawai")

    if gpu:
        node_color = [
            [colors[m % len(colors)] for m in y]
            for y in [y_true_G, y_cpu_G, y_gpu_G]
        ]

        tx.draw(
            [G, G, G], figsize=(6, 2.5), pos=pos, node_size=50,
            title=["CPU", "Ground Truth (Static)", "GPU"],
            temporal_node_color=node_color)

    log.info("Temporal graph optimization")
    y_true_TG = tx.get_node_attributes(TG, "community", index=False)
    pos = tx.layout(TG, layout="kamada_kawai")

    if gpu:
        temporal_node_color = [
            [colors[m % len(colors)] for m in s]
            for y in [y_true_TG, y_cpu_TG, y_gpu_TG, y_gpu_TG_norefine, y_gpu_G_supra]
            for s in y
        ]

        title = [
            "", "Ground Truths (Temporal)", "",
            "", "CPU", "",
            "", "GPU", "",
            "", "GPU (No Refine)", "",
            "", "GPU (Supra)", "",
        ]

        tx.draw(
            [*TG, *TG, *TG, *TG, *TG], figsize=(6, 9.5), nrows=5, ncols=3,
            pos=[*pos, *pos, *pos, *pos, *pos], node_size=50, title=title,
            temporal_node_color=temporal_node_color)

    log.info("Supra-graph optimization")
    T, omega = len(TG), 1.0

    # Normalize and symmetrize inter-slice couplings based on inverse distance weighting.
    raw = {(i, j): 1 / abs(i - j) for i in range(T) for j in range(T) if i != j}
    row = {i: sum(raw[(i, k)] for k in range(T) if k != i) for i in range(T)}
    w = {(i, j): omega * v * 0.5 * (1 / row[i] + 1 / row[j]) for (i, j), v in raw.items()}

    # Build supra-graph connecting nodes across 'all' time slices.
    adj, offsets = tx.to_supra_adjacency_matrix(
        TG, interslice_couple="all", interslice_weights=w, return_offsets=True)

    # Supra-graph (static) modularity optimization.
    G_supra_ = tx.from_scipy(adj)
    if gpu:
        y_gpu_G_supra_ = tx.leiden_communities(G_supra_, max_iter=max_iter, device="gpu")
        y_gpu_G_supra_ = [y_gpu_G_supra_[offsets[t]:offsets[t] + len(TG[t])]
                          for t in range(len(TG))]

    assert str(G) == "MultiGraph with 75 nodes and 589 edges"
    assert str(G_supra) == "MultiGraph with 225 nodes and 690 edges"
    assert str(G_supra_) == "MultiGraph with 225 nodes and 765 edges"

    if gpu:
        temporal_node_color = [
            [colors[m % len(colors)] for m in s]
            for y in [y_true_TG, y_gpu_G_supra, y_gpu_G_supra_]
            for s in y
        ]

        title = [
            "", "Ground Truths (Temporal)", "",
            "", "GPU (Supra)", "",
            "", "GPU (Supra, Coupling 'all' Slices, Reweighted)", "",
        ]

        tx.draw(
            [*TG, *TG, *TG], figsize=(6, 6), nrows=3, ncols=3,
            pos=[*pos, *pos, *pos], node_size=50, title=title,
            temporal_node_color=temporal_node_color)

    plt.close("all")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--log-level",
                        choices=["debug", "info", "warning", "error", "critical"],
                        default="info",
                        help="Set the logging level.")

    parser.add_argument("--gpu",
                        action="store_true",
                        dest="test_gpu",
                        help="Run GPU acceleration examples (requires CuPy/cuGraph).")

    parser.add_argument("--pubmed",
                        action="store_true",
                        dest="test_pubmed",
                        help="Run PubMed dataset examples (slow on CPU).")

    args = parser.parse_args()
    log_level = args.__dict__.pop("log_level")

    if log_level is not None:
        log.basicConfig(format=LOG_FORMAT, level=getattr(log, log_level.upper()))

    test_docs(**vars(args))
