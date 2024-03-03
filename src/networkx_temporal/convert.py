from typing import Literal

import networkx as nx

try:
    import dgl
    nx2dgl = dgl.from_networkx
except ImportError:
    nx2dgl = None

try:
    from .utils.nx2gt import nx2gt
except ImportError:
    nx2gt = None

try:
    import igraph as ig
    nx2ig = ig.Graph.from_networkx
except ImportError:
    nx2ig = None

try:
    import networkit as nk
    nx2nk = nk.nxadapter.nx2nk
except ImportError:
    nx2nk = None

try:
    from .utils.nx2snap import nx2snap
except ImportError:
    nx2snap = None

try:
    import torch_geometric as pyg
    nx2pyg = pyg.utils.convert.from_networkx
except ImportError:
    nx2pyg = None

TO_DICT = {
    "dgl": "dgl",
    "gt": "graph_tool",
    "ig": "igraph",
    "nk": "networkit",
    "pyg": "torch_geometric",
    "snap": "snap"
}

TO_LITERAL = Literal[
    "dgl",
    "graph_tool",
    "igraph",
    "networkit",
    "torch_geometric"
    "snap",
]


def convert_to(G: nx.Graph, to: TO_LITERAL, *args, **kwargs):
    """
    Returns converted NetworkX graph object.

    Accepted packages:
    - "dgl": Deep Graph Library
    - "gt": Graph Tool
    - "ig": iGraph
    - "nk": Networkit
    - "pyg": PyTorch Geometric
    - "snap": Stanford Network Analysis Platform (not implemented)

    :param G: NetworkX graph object.
    :param to: Package to convert the graph to.
    :param args: Additional arguments for the conversion.
    :param kwargs: Additional keyword arguments for the conversion.
    """
    to = TO_DICT.get(to, to)
    to_short = {v: k for k, v in TO_DICT.items()}.get(to)

    assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `G` must be a NetworkX graph object, received: {type(G)}."

    assert to in TO_LITERAL.__args__,\
        f"Argument `to` must be in {TO_LITERAL.__args__}."

    assert globals()[f"nx2{to_short}"] is not None,\
        f"Package '{to}' is not installed."

    return globals()[f"nx2{to_short}"](G, *args, **kwargs)
