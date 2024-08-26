#!/usr/bin/env python

import logging as log
from argparse import ArgumentParser
from io import BytesIO
from os import remove
from typing import Optional

import networkx_temporal as tx
from networkx_gdf import read_gdf, write_gdf
from networkx_temporal.convert import FORMATS
from networkx_temporal.typing import Literal

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVELS = Literal["debug", "info", "warning", "error", "critical"]


def test_networkx_temporal(log_level: Optional[str] = None, convert: list = []) -> None:
    if log_level is not None:
        log.basicConfig(format=LOG_FORMAT, level=getattr(log, log_level.upper()))

    TG = tx.TemporalGraph(directed=True, multigraph=True)

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
    assert len(TG) == 4
    assert len(TG.slice(bins=2)) == 2
    assert TG.order() == [2, 3, 4, 4]
    assert TG.size() == [1, 2, 3, 3]
    assert TG.temporal_order() == 6
    assert TG.total_order() == 13
    assert TG.temporal_size() == TG.total_size() == 9
    assert TG.temporal_degree() == {"a": 4, "b": 4, "c": 3, "d": 2, "e": 2, "f": 3}
    assert TG.temporal_degree("a") == 4
    assert TG.temporal_neighbors("c") == set("b")
    assert TG.to_undirected().is_directed() == False
    assert TG.to_directed().is_directed() == True

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
    ETG = TG.to_events()
    TG_ = tx.from_events(ETG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # TG -> UTG -> TG
    log.info("TG -> UTG -> TG")
    UTG = TG.to_unified()
    TG_ = tx.from_unified(UTG)
    assert TG.order() == TG_.order()
    assert TG.size() == TG_.size()

    # {TG,G} -> pkg
    for pkg in [pkg for pkg in FORMATS.__args__ if pkg in convert or "all" in convert]:
        log.info(f"TG -> {pkg}")
        tx.convert(TG, to=pkg)
        log.info(f"G -> {pkg}")
        tx.convert(G, to=pkg)

    print("All tests passed!")
    remove("temporal-graph.graphml.zip")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--log-level",
                        choices=LOG_LEVELS.__args__,
                        help="Set the logging level.")

    parser.add_argument("--convert",
                        default=[],
                        dest="convert",
                        nargs="+",
                        help="Perform conversion tests for specified (or 'all') packages.")

    args = parser.parse_args()

    test_networkx_temporal(**vars(args))
