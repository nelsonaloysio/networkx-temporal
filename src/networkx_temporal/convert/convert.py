from importlib import import_module
from typing import Any, Union

import networkx as nx

from ..typing import TemporalGraph, Literal

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


def convert(TG: Union[nx.Graph, TemporalGraph], to: FORMATS, *args, **kwargs) -> Any:
    """
    Returns converted graph object.

    The ``to`` parameter supports the following packages and their respective aliases:

    +------------------------------------------------------------------+------------------------------------+------------------------+
    | Format                                                           | Parameter (Package)                | Parameter (Alias)      |
    +==================================================================+====================================+========================+
    |`Deep Graph Library <https://www.dgl.ai/>`__                      | .. centered :: ``dgl``             | .. centered :: -       |
    +------------------------------------------------------------------+------------------------------------+------------------------+
    |`graph-tool <https://graph-tool.skewed.de/>`__                    | .. centered :: ``graph_tool``      | .. centered :: ``gt``  |
    +------------------------------------------------------------------+------------------------------------+------------------------+
    |`igraph <https://igraph.org/python/>`__                           | .. centered :: ``igraph``          | .. centered :: ``ig``  |
    +------------------------------------------------------------------+------------------------------------+------------------------+
    |`NetworKit <https://networkit.github.io/>`__                      | .. centered :: ``networkit``       | .. centered :: ``nk``  |
    +------------------------------------------------------------------+------------------------------------+------------------------+
    |`PyTorch Geometric <https://pytorch-geometric.readthedocs.io>`__  | .. centered :: ``torch_geometric`` | .. centered :: ``pyg`` |
    +------------------------------------------------------------------+------------------------------------+------------------------+
    |`Teneto <https://teneto.readthedocs.io>`__                        | .. centered :: ``teneto``          | .. centered :: -       |
    +------------------------------------------------------------------+------------------------------------+------------------------+

    .. important::

       To reduce package dependencies and avoid unnecessary imports, the required library is
       imported on function call based on the ``to`` parameter and must be separately installed.

    :param TG: Temporal or static graph object.
    :param str to: Package name or alias to convert the graph object.
    :param args: Additional positional arguments for the conversion function.
    :param kwargs: Additional keyword arguments for the conversion function.

    :return: Converted graph object.
    """
    pkg = ALIAS.get(to, to)
    func = "nx2%s" % {v: k for k, v in ALIAS.items()}.get(pkg, pkg)

    assert pkg in FORMATS.__args__,\
        f"Argument `to` must be among packages {FORMATS.__args__} or aliases {list(ALIAS)}."

    try:
        func = import_module(f".{func}", package=__package__).__dict__[func]
    except ImportError as e:
        raise e

    if type(TG) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
        return func(TG, *args, **kwargs)

    return [func(G, *args, **kwargs) for G in TG]
