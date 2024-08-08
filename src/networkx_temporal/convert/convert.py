from importlib import import_module
from typing import Literal

import networkx as nx

ALIAS = {
    "gt": "graph_tool",
    "ig": "igraph",
    "nk": "networkit",
    "pyg": "torch_geometric",
}

FORMATS = Literal[
    "dgl",
    "graph_tool",
    "igraph",
    "networkit",
    "torch_geometric",
    "snap",
    "teneto",
]


def convert(G: nx.Graph, to: FORMATS, *args, **kwargs):
    """
    Returns converted NetworkX graph object.

    Accepted formats:
    - `"dgl"`: Deep Graph Library
    - `"gt"`: Graph Tool
    - `"ig"`: iGraph
    - `"nk"`: NetworKit
    - `"pyg"`: PyTorch Geometric
    - `"snap"`: Stanford Network Analysis Platform
    - `"teneto"`: Teneto

    :param G: NetworkX graph object.
    :param to: Format to convert the graph.
    :param args: Additional arguments for the conversion.
    :param kwargs: Additional keyword arguments for the conversion.
    """
    pkg = ALIAS.get(to, to)
    func = "nx2%s" % {v: k for k, v in ALIAS.items()}.get(pkg, pkg)

    assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `G` must be a networkx or temporal-networkx graph object, received: {type(G)}."

    assert pkg in FORMATS.__args__,\
        f"Argument `to` must be in {FORMATS.__args__} or aliases {list(ALIAS)}."

    try:
        func = import_module(f".{func}", package=__package__).__dict__[func]
    except ImportError as e:
        raise e

    return func(G, *args, **kwargs)
