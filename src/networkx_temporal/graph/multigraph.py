from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalMultiGraph(TemporalBase, nx.MultiGraph if nx.__version__ >= "2.8.1" else object):
    """
    Creates a temporal undirected multigraph. Allows parallel edges among the same pair of nodes.

    It inherits a static NetworkX `MultiGraph
    <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
    and includes all methods available from it, such as :func:`add_node`, :func:`add_edge`,
    :func:`neighbors`, :func:`subgraph`, :func:`to_directed`, and :func:`to_undirected`,
    as well as additional methods implemented for handling temporal graphs and snapshots.

    This is equivalent to calling :func:`~networkx_temporal.graph.temporal_graph` with ``directed=False``
    and ``multigraph=True``.

    .. seealso::

       The :class:`~networkx_temporal.graph.TemporalGraph` class documentation
       for details on its implemented methods.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.

    :note: Documentation on inherited methods is available only if ``networkx>=2.8.1``.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=True)
