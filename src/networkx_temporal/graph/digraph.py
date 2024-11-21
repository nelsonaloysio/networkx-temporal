from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalDiGraph(TemporalBase, nx.DiGraph if nx.__version__ >= "2.8.1" else object):
    """
    Creates a temporal directed graph. Does not allow parallel edges among node pairs.

    It inherits a static NetworkX `DiGraph
    <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__
    and includes all methods available from it, such as :func:`add_node`, :func:`add_edge`,
    :func:`neighbors`, :func:`subgraph`, :func:`to_directed`, and :func:`to_undirected`,
    as well as additional methods implemented for handling temporal graphs and snapshots.

    This is equivalent to calling :func:`~networkx_temporal.graph.temporal_graph` with ``directed=True``
    and ``multigraph=False``.

    .. seealso::

       The :class:`~networkx_temporal.graph.TemporalGraph` class documentation
       for details on its implemented methods.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.

    :note: Documentation on inherited methods is available only if ``networkx>=2.8.1``.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=True, multigraph=False)
