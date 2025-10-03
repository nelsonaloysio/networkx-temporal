#!/usr/bin/env python

from datetime import datetime

import networkx_temporal as tx
from nx_hif.readwrite import read_hif

DATA_PATH = "data/publications.hif.json"


def test_hif():
    # Hypergraph Interchange Format (HIF) standard
    # https://pypi.org/project/nx-hif
    H = read_hif("data/publications.hif.json")
    TG = tx.readwrite.read_hif(DATA_PATH)
    TG = TG.slice(attr="date", apply_func=lambda x: datetime.fromisoformat(x).timestamp())
    assert H.order() == TG.order(copies=False) == 2493
    assert H.size() == TG.size(copies=True) == 2301
    assert len(TG) == 119
    print("All tests passed!")


if __name__ == "__main__":
    test_hif()
