from typing import Literal

import networkx as nx

try:
    import dgl
    nx2dgl = dgl.from_networkx
except ImportError:
    nx2dgl = None

try:
    from ..utils.nx2gt import nx2gt
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
    from ..utils.nx2snap import nx2snap
except ImportError:
    nx2snap = None

try:
    import torch_geometric as pyg
    nx2pyg = pyg.utils.convert.from_networkx
except ImportError:
    nx2pyg = None

try:
    from ..utils.nx2teneto import nx2teneto
except ImportError:
    nx2teneto = None

ALIAS = {
    "gt": "graph_tool",
    "ig": "igraph",
    "nk": "networkit",
    "pyg": "torch_geometric",
}

FORMAT = Literal[
    "dgl",
    "graph_tool",
    "igraph",
    "networkit",
    "torch_geometric"
    "snap",
    "teneto"
]


def convert(G: nx.Graph, to: FORMAT, *args, **kwargs):
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
    :param to: Format to convert the graph to.
    :param args: Additional arguments for the conversion.
    :param kwargs: Additional keyword arguments for the conversion.
    """
    to = ALIAS.get(to, to)
    func = "nx2%s" % {v: k for k, v in ALIAS.items()}.get(to, to)

    assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `G` must be a networkx or temporal-networkx graph object, received: {type(G)}."

    assert to in FORMAT.__args__,\
        f"Argument `to` must be in {FORMAT.__args__}."

    assert globals()[func] is not None,\
        f"Package '{to}' is not installed."

    return globals()[func](G, *args, **kwargs)
