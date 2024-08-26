from typing import Optional

import networkx as nx

from .base import TemporalBase


class TemporalGraph(TemporalBase, nx.Graph):
    """
    Creates a temporal undirected graph.

    It inherits a static NetworkX `Graph
    <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
    and includes all methods implemented by it, such as ``add_node``, ``add_edge``,
    ``neighbors``, ``remove_node``, ``remove_edge``, ``subgraph``, ``to_directed``, and
    ``to_undirected``, as well as additional methods for handling temporal graphs and
    snapshots.

    This is equivalent to calling :func:`~networkx_temporal.temporal_graph` with ``directed=False``
    and ``multigraph=False``.


    .. seealso::

       * The `official NetworkX documentation
         <https://networkx.org/documentation/stable/reference/classes/index.html>`__
         for a list of methods available for each graph type.
       * The `Examples: Basic operations
         <https://networkx-temporal.readthedocs.io/en/latest/examples.html>`__
         page for more examples on building a temporal graph.

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

       Setting ``t`` greater than ``1`` will create a list of NetworkX graph objects, each
       representing a snapshot in time. Unless dynamic node attributes are required, it is
       recommended to use the :func:`~networkx_temporal.TemporalGraph.slice` method instead,
       in order to create less resource-demanding graph `views
       <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
       on the fly.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.
    """
    def __init__(self, t: Optional[int] = None):
        super().__init__(t=t, directed=False, multigraph=False)
