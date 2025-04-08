#!/usr/bin/env python

import logging as log
from argparse import ArgumentParser
from io import BytesIO
from os import remove
from typing import Optional

import networkx_temporal as tx
from networkx_temporal.typing import Literal
from networkx_temporal.utils.convert import FORMATS

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVELS = Literal


def test_networkx_temporal(test_convert: bool = False) -> None:
    """ Test networkx-temporal package. """
    TG = tx.temporal_graph(directed=True, multigraph=True)
    assert TG.is_directed()
    assert TG.is_multigraph()
    assert tx.is_temporal_graph(TG)
    assert not tx.from_multigraph(TG).is_multigraph()
    assert tx.to_multigraph(tx.from_multigraph(TG)).is_multigraph()
    assert type(TG) == tx.TemporalMultiDiGraph

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

    # TG
    log.info("TG")
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
    assert tx.degree_centrality(TG, "a") == 0.8
    assert tx.degree_centralization(TG) == [0, 1.0, 0.3333333333333333, 1.0]
    assert list(TG.neighbors("c")) == [[], ['b'], [], []]
    assert list(tx.neighbors(TG, "c")) == ["b"]
    assert TG.to_directed().is_directed()
    assert not TG.to_undirected().is_directed()
    assert order == TG.order()
    assert size == TG.size()

    # TG.copy()
    TG_ = TG.copy()
    TG_[-1].add_edge("g", "h")
    assert TG_.order()[-1] == TG.order()[-1] + 2
    assert TG_.size()[-1] == TG.size()[-1] + 1

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
    ETG = TG.copy().to_events(eps=int)
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()
    ETG = TG.copy().to_events(eps=float)
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> UTG -> TG
    log.info("TG -> UTG -> TG")
    UTG = TG.to_unrolled()
    TG_ = tx.from_unrolled(UTG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # {TG,G} -> pkg
    if test_convert:
        for pkg in FORMATS.__args__:
            log.info("TG -> %s", pkg)
            tx.convert(TG, to=pkg)
            log.info("G -> %s", pkg)
            tx.convert(G, to=pkg)

    print("All tests passed!")
    remove("temporal-graph.graphml.zip")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--log-level",
                        choices=["debug", "info", "warning", "error", "critical"],
                        default="info",
                        help="Set the logging level.")

    parser.add_argument("--convert",
                        action="store_true",
                        dest="test_convert",
                        help="Perform conversion tests to other packages.")

    args = parser.parse_args()
    log_level = args.__dict__.pop("log_level")

    if log_level is not None:
        log.basicConfig(format=LOG_FORMAT, level=getattr(log, log_level.upper()))

    test_networkx_temporal(**vars(args))
