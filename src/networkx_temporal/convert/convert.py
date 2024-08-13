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
    "teneto",
]


def convert(G: nx.Graph, to: FORMATS, *args, **kwargs):
    """
    Returns converted NetworkX graph object.

    Note that the required package for the conversion is imported on function
    call based on the given argument parameter. This is done to reduce the
    dependencies of the package and to avoid unnecessary imports.

    Supported packages and their respective aliases:

    +-----------------------------------------------------------------+------------------------------------+------------------------+
    | Format                                                          | Parameter (Package)                | Parameter (Alias)      |
    +=================================================================+====================================+========================+
    |`Deep Graph Library <https://www.dgl.ai/>`_                      | .. centered :: ``dgl``             | .. centered :: -       |
    +-----------------------------------------------------------------+------------------------------------+------------------------+
    |`graph-tool <https://graph-tool.skewed.de/>`_                    | .. centered :: ``graph_tool``      | .. centered :: ``gt``  |
    +-----------------------------------------------------------------+------------------------------------+------------------------+
    |`igraph <https://igraph.org/python/>`_                           | .. centered :: ``igraph``          | .. centered :: ``ig``  |
    +-----------------------------------------------------------------+------------------------------------+------------------------+
    |`NetworKit <https://networkit.github.io/>`_                      | .. centered :: ``networkit``       | .. centered :: ``nk``  |
    +-----------------------------------------------------------------+------------------------------------+------------------------+
    |`PyTorch Geometric <https://pytorch-geometric.readthedocs.io>`_  | .. centered :: ``torch_geometric`` | .. centered :: ``pyg`` |
    +-----------------------------------------------------------------+------------------------------------+------------------------+
    |`Teneto <https://teneto.readthedocs.io>`_                        | .. centered :: ``teneto``          | .. centered :: -       |
    +-----------------------------------------------------------------+------------------------------------+------------------------+

    :param G: NetworkX graph object.
    :param str to: Format to convert data to.
    :param args: Additional positional arguments for the conversion.
    :param kwargs: Additional keyword arguments for the conversion.

    :return: Converted graph object.
    :rtype: Any
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
