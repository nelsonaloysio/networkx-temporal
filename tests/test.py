#!/usr/bin/env python

import logging as log
from argparse import ArgumentParser
from io import BytesIO
from os import remove

import networkx_temporal as tx
from networkx_temporal.typing import Literal, TemporalGraph
from networkx_temporal.utils.convert import FORMATS

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVELS = Literal


def test_networkx_temporal(*args, **kwargs) -> None:
    log.info("test_networkx_temporal")
    test_convert = kwargs.pop("test_convert", False)

    TG = test_temporal_graph()
    test_copy_graph(TG)
    test_write_graph(TG)
    test_transform_graph(TG)
    test_degree_vectors()
    test_dynamic_sbm()
    test_generators()

    if test_convert:
        for pkg in test_convert:
            assert pkg in FORMATS.__args__, f"Unsupported package: '{pkg}' not in {FORMATS.__name__}"
            test_convert_graph(TG, pkg)

    print("All tests passed!")


def test_temporal_graph() -> TemporalGraph:
    log.info("test_temporal_graph")
    # temporal_graph
    TG = tx.temporal_graph(directed=True, multigraph=True)
    TG.add_edges_from([
        ("a", "b", {"time": 0}),
        ("a", "b", {"time": 1}),
        ("c", "b", {"time": 1}),
        ("d", "c", {"time": 2}),
        ("d", "e", {"time": 2}),
        ("a", "c", {"time": 2}),
        ("f", "e", {"time": 3}),
        ("f", "a", {"time": 3}),
        ("f", "b", {"time": 3}),
    ])
    assert TG.is_directed()
    assert TG.is_multigraph()
    assert tx.is_temporal_graph(TG)
    assert not tx.from_multigraph(TG).is_multigraph()
    assert tx.to_multigraph(tx.from_multigraph(TG)).is_multigraph()
    assert type(TG) == tx.TemporalMultiDiGraph
    TG = TG.slice(attr="time")
    order = TG.order()
    size = TG.size()
    assert len(TG.flatten()) == 1
    assert len(TG) == 4
    assert len(TG.slice(bins=2)) == 2
    assert TG.order() == [2, 3, 4, 4]
    assert TG.size() == [1, 2, 3, 3]
    assert TG.temporal_order() == TG.order(copies=False) == 6
    assert TG.temporal_size() == TG.size(copies=False) == 8
    assert TG.total_order() == TG.order(copies=True) == 13
    assert TG.total_size() == TG.size(copies=True) == 9
    assert TG.total_degree() == {"a": 4, "b": 4, "c": 3, "d": 2, "e": 2, "f": 3}
    assert TG.total_degree("a") == 4
    assert TG.total_in_degree("a") == 1
    assert TG.total_out_degree("a") == 3
    assert TG.total_degree() == TG.total_degree()
    assert TG.total_in_degree() == TG.total_in_degree()
    assert TG.total_out_degree() == TG.total_out_degree()
    assert tx.degree_centrality(TG, "a") == 0.8
    assert tx.degree_centralization(TG) == [0, 1.0, 0.3333333333333333, 1.0]
    assert list(TG.neighbors("c")) == [[], ['b'], [], []]
    assert list(tx.neighbors(TG, "c")) == ["b"]
    assert TG.to_directed().is_directed()
    assert not TG.to_undirected().is_directed()
    assert order == TG.order()
    assert size == TG.size()
    return TG


def test_copy_graph(TG) -> None:
    log.info("test_copy_graph")
    TG_ = TG.copy()
    TG_[-1].add_edge("g", "h")
    assert TG_.order()[-1] == TG.order()[-1] + 2
    assert TG_.size()[-1] == TG.size()[-1] + 1


def test_write_graph(TG) -> None:
    log.info("test_write_graph")
    # TG -> path -> TG
    log.info("TG -> path -> TG")
    tx.write_graph(TG, "temporal-graph.graphml.zip")
    TG_ = tx.read_graph("temporal-graph.graphml.zip")
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> file -> TG
    log.info("TG -> file -> TG")
    with open("temporal-graph.graphml.zip", "wb") as f:
        tx.write_graph(TG, f)
    with open("temporal-graph.graphml.zip", "rb") as f:
        TG_ = tx.read_graph(f)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()
    remove("temporal-graph.graphml.zip")

    # TG -> buffer -> TG
    log.info("TG -> buffer -> TG")
    bio = BytesIO()
    buffer = tx.write_graph(TG, bio)
    TG_ = tx.read_graph(bio)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> bytes -> TG
    log.info("TG -> bytes -> TG")
    buffer = tx.write_graph(TG)
    TG_ = tx.read_graph(buffer)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()


def test_transform_graph(TG) -> None:
    log.info("test_transform_graph")
    # TG -> G -> TG
    log.info("TG -> G -> TG")
    G = TG.to_static()
    TG_ = tx.from_static(G).slice(attr="time")
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> STG -> TG
    log.info("TG -> STG -> TG")
    STG = TG.to_snapshots()
    TG_ = tx.from_snapshots(STG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> ETG -> TG
    log.info("TG -> ETG -> TG")
    ETG = TG.copy().to_events()
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()
    ETG = TG.copy().to_events(delta=int)
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()
    ETG = TG.copy().to_events(delta=float)
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> UTG -> TG
    log.info("TG -> UTG -> TG")
    UTG = TG.to_unrolled()
    TG_ = tx.from_unrolled(UTG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()


def test_degree_vectors() -> None:
    d1 = tx.generators.generate_degree_vector(100, max_degree=20, seed=0)
    d2 = tx.generators.generate_degree_vector(100, max_degree=20, phi=6, seed=0)
    d3 = tx.generators.generate_degree_vector(100, max_degree=20, alpha=2, seed=0)
    assert sum(d1)/len(d1) == 9.88
    assert sum(d2)/len(d2) == 10.15
    assert sum(d3)/len(d3) == 2.56


def test_dynamic_sbm() -> None:
    log.info("test_dynamic_sbm")
    n, k = 5, 2
    TG = tx.generators.dynamic_sbm(
        B=tx.generators.generate_block_matrix(k),
        z=tx.generators.generate_community_vector(n, k),
        d=tx.generators.generate_degree_vector(n*k, seed=0),
        transition_matrix=tx.generators.generate_transition_matrix(k, eta=0.9),
        t=2,
        seed=0,
        sparse=True
    )
    clusters = [
        [len([i for i in community_t if i == c]) for c in set(community_t)]
        for community_t in [[c for n, c in G.nodes(data="community")] for G in TG]
    ]
    assert TG.order() == [10, 10]
    assert TG.order(copies=True) == 20
    assert TG.order(copies=False) == 10
    # assert TG.size() == [38, 32]
    # assert TG.size(copies=True) == 70
    # assert TG.size(copies=False) == 38
    assert TG.size() == [42, 40]
    assert TG.size(copies=True) == 82
    assert TG.size(copies=False) == 44
    assert clusters == [[5, 5], [6, 4]]


def test_generators() -> None:
    log.info("test_generators")
    d = tx.generators.generate_degree_vector(10, max_degree=10, seed=0)
    assert d.tolist() == [6, 1, 4, 4, 8, 10, 4, 6, 3, 5]
    z = tx.generators.generate_community_vector(5, 2, shuffle=True, seed=0)
    assert z.tolist() == [0, 1, 0, 1, 0, 1, 1, 0, 0, 1]
    Z = tx.generators.generate_community_matrix(3, 2, shuffle=True, seed=0)
    assert Z.tolist() == [[0.0, 1.0], [1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]]
    B = tx.generators.generate_block_matrix(2, p=0.8, q=0.2)
    assert B.tolist() == [[0.8, 0.2], [0.2, 0.8]]
    tau = tx.generators.generate_transition_matrix(2, eta=[.6, .3], uniform_all=False)
    assert tau.tolist() == [[0.6, 0.4], [0.7, 0.3]]
    z_ = tx.generators.transition_node_memberships(z, tau, seed=0)
    assert z_.tolist() == [0, 1, 1, 0, 0, 0, 0, 1, 1, 0]
    Z_ = tx.generators.transition_node_memberships(Z, tau, seed=0)
    assert Z_.tolist() == [0, 1, 1, 0, 0, 0]


def test_convert_graph(TG, pkg) -> None:
    log.info("test_convert_graph")
    # TG -> graph
    log.info("TG -> %s", pkg)
    tx.convert(TG, to=pkg)
    G = tx.to_static(TG)
    log.info("G -> %s", pkg)
    tx.convert(G, to=pkg)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--log-level",
                        choices=["debug", "info", "warning", "error", "critical"],
                        default="info",
                        help="Set the logging level.")

    parser.add_argument("--convert",
                        choices=FORMATS.__args__,
                        default=False,
                        dest="test_convert",
                        help="Perform conversion tests to other packages.",
                        nargs="+")

    args = parser.parse_args()
    log_level = args.__dict__.pop("log_level")

    if log_level is not None:
        log.basicConfig(format=LOG_FORMAT, level=getattr(log, log_level.upper()))

    test_networkx_temporal(**vars(args))
