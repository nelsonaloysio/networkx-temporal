from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalMultiGraph(TemporalBase, nx.MultiGraph):
    """
    Creates a temporal undirected multigraph.

    It inherits a static NetworkX `MultiGraph
    <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
    and includes all methods implemented by it, such as ``add_node``, ``add_edge``,
    ``neighbors``, ``remove_node``, ``remove_edge``, ``subgraph``, ``to_directed``, and
    ``to_undirected``, as well as additional methods for handling temporal graphs and
    snapshots.

    This is equivalent to calling :func:`~networkx_temporal.temporal_graph` with ``directed=False``
    and ``multigraph=True``.

    .. seealso::

       The :class:`~networkx_temporal.graph.graph.TemporalGraph` class documentation
       for details on the implemented methods.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=True)
