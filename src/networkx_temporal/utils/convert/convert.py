from importlib import import_module
from typing import Any, Union
from warnings import warn

from ...typing import Literal, StaticGraph, TemporalGraph

ALIASES = {
    "dn": "dynetx",
    "gt": "graph_tool",
    "ig": "igraph",
    "nk": "networkit",
    "pyg": "torch_geometric",
    "sg": "stellargraph",
    "tn": "teneto",
}

FORMATS = Literal[
    "dgl",
    "dynetx",
    "graph_tool",
    "igraph",
    "networkit",
    "snap",
    "stellargraph",
    "torch_geometric",
    "teneto",
]


def convert(G: Union[TemporalGraph, StaticGraph, list], to: FORMATS, *args, **kwargs) -> Any:
    """
    High-level conversion function to other libraries. Calls the appropriate function based on the
    received ``to`` parameter. The following graph libraries are currently supported for conversion:

    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | Format                                                            | Parameter (Package)                  | .. centered:: Calls (Function)                                            |
    +===================================================================+======================================+===========================================================================+
    | `Deep Graph Library <https://www.dgl.ai>`__                       | .. centered:: ``'dgl'``              | .. centered:: :func:`~networkx_temporal.utils.convert.to_dgl`             |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `DyNetX <https://dynetx.readthedocs.io>`__                        | .. centered:: ``'dynetx'``           | .. centered:: :func:`~networkx_temporal.utils.convert.to_dynetx`          |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `graph-tool <https://graph-tool.skewed.de>`__                     | .. centered:: ``'graph_tool'``       | .. centered:: :func:`~networkx_temporal.utils.convert.to_graph_tool`      |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `igraph <https://igraph.org/python>`__                            | .. centered:: ``'igraph'``           | .. centered:: :func:`~networkx_temporal.utils.convert.to_igraph`          |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `NetworKit <https://networkit.github.io>`__                       | .. centered:: ``'networkit'``        | .. centered:: :func:`~networkx_temporal.utils.convert.to_networkit`       |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `PyTorch Geometric <https://pytorch-geometric.readthedocs.io>`__  | .. centered:: ``'torch_geometric'``  | .. centered:: :func:`~networkx_temporal.utils.convert.to_torch_geometric` |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `SNAP <https://https://snap.stanford.edu>`__                      | .. centered:: ``'snap'``             | .. centered:: :func:`~networkx_temporal.utils.convert.to_snap`            |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `StellarGraph <https://stellargraph.readthedocs.io>`__            | .. centered:: ``'stellargraph'``     | .. centered:: :func:`~networkx_temporal.utils.convert.to_stellargraph`    |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+
    | `Teneto <https://teneto.readthedocs.io>`__                        | .. centered:: ``'teneto'``           | .. centered:: :func:`~networkx_temporal.utils.convert.to_teneto`          |
    +-------------------------------------------------------------------+--------------------------------------+---------------------------------------------------------------------------+

    .. note::

       To reduce package dependencies and avoid unnecessary imports, the required library is
       imported on function call based on the ``to`` parameter and must be separately installed.

    .. rubric:: Example

    Convert the `Karate Club
    <https://networkx.org/documentation/stable/auto_examples/graph/plot_karate_club.html>`__
    dataset from NetworkX into a PyTorch Geometric `Data
    <https://pytorch-geometric.readthedocs.readwrite/en/latest/generated/torch_geometric.data.Data.html>`__
    object:

    .. code-block:: python

        >>> import networkx as nx
        >>> import networkx_temporal as tx
        >>>
        >>> G = nx.karate_club_graph()
        >>> data = tx.convert(G, "pyg")
        >>>
        >>> print(G)
        >>> print(data)

        Graph named "Zachary's Karate Club" with 34 nodes and 78 edges
        Data(edge_index=[2, 156], club=[34], weight=[156], name='Zachary's Karate Club', num_nodes=34)

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param str to: Package name or alias to convert the graph object.
    :param args: Additional positional arguments for the conversion function.
    :param kwargs: Additional keyword arguments for the conversion function.

    :rtype: Any

    :note: Available both as a function and as a method from :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    pkg = ALIASES.get(to, to)
    func = ALIASES.get(pkg, pkg)

    if to in ALIASES:
        warn(
            f"Alias '{to}' for '{pkg}' is deprecated and will be removed in future versions.",
            category=FutureWarning
        )

    assert pkg in FORMATS.__args__,\
        f"Argument `to` must be among {list(FORMATS.__args__)} or aliases {list(ALIASES)}."

    func = import_module(f".", package=__package__).__dict__["to_%s" % func]
    return func(G, *args, **kwargs)
