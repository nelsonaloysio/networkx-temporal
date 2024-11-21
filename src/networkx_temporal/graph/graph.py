from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalGraph(TemporalBase, nx.Graph if nx.__version__ >= "2.8.1" else object):
    """
    Creates a temporal undirected graph. Does not allow parallel edges among node pairs.

    It inherits a static NetworkX `Graph
    <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
    and includes all methods available from it, such as :func:`add_node`, :func:`add_edge`,
    :func:`neighbors`, :func:`subgraph`, :func:`to_directed`, and :func:`to_undirected`,
    as well as additional methods implemented for handling temporal graphs and snapshots.

    This is equivalent to calling :func:`~networkx_temporal.graph.temporal_graph` with ``directed=False``
    and ``multigraph=False``.

    .. seealso::

       - The `Examples → Basic operations
         <../examples/basics.html#build-temporal-graph>`__
         page for examples on building a temporal graph.
       - The `official NetworkX documentation
         <https://networkx.org/documentation/stable/reference/classes/index.html>`__
         for a list of methods inherited by this class.
       - The :class:`~networkx_temporal.graph.TemporalDiGraph`,
         :class:`~networkx_temporal.graph.TemporalMultiGraph`,
         and :class:`~networkx_temporal.graph.TemporalMultiDiGraph` classes for other temporal graph types
         with directed and/or multiple edges among node pairs.

    .. rubric:: Example

    The following example demonstrates how to create a temporal graph with two snapshots:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalGraph(t=2)
       >>> # TG = tx.temporal_graph(t=2, directed=False, multigraph=False)
       >>>
       >>> TG[0].add_edge("a", "b")
       >>> TG[1].add_edge("c", "b")
       >>>
       >>> print(TG)

       TemporalGraph (t=2) with 4 nodes and 2 edges

    .. hint::

       Setting ``t`` as greater than ``1`` initializes a list of NetworkX graph objects, each
       representing a snapshot in time. Unless dynamic node attributes are required, it is
       recommended to use the :func:`~networkx_temporal.graph.TemporalGraph.slice` method instead,
       allowing to create less resource-demanding graph `views
       <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
       on the fly.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.

    :note: Documentation on inherited methods is available only if ``networkx>=2.8.1``.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=False)
