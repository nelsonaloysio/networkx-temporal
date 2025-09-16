.. include:: ../include-examples.rst


################
Basic operations
################

The examples below cover the package's basic functionalities, including how to build a temporal
graph, slice it into snapshots, save and load graph objects to disk, and other inherited methods.


Build temporal graph
====================

This package implements new
:class:`~networkx_temporal.classes.TemporalGraph`
classes, which extend `NetworkX graphs
<https://networkx.org/documentation/stable/reference/classes/index.html>`__
to handle temporal (dynamic) data.
Let's start by creating a simple directed graph using ``time`` as attribute key:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalMultiDiGraph()
   >>> # TG = tx.temporal_graph(directed=True, multigraph=True)
   >>>
   >>> TG.add_edge("a", "b", time=0)
   >>> TG.add_edge("c", "b", time=1)
   >>> TG.add_edge("d", "c", time=2)
   >>> TG.add_edge("d", "e", time=2)
   >>> TG.add_edge("a", "c", time=2)
   >>> TG.add_edge("f", "e", time=3)
   >>> TG.add_edge("f", "a", time=3)
   >>> TG.add_edge("f", "b", time=3)
   >>>
   >>> print(TG)

   TemporalMultiDiGraph (t=1) with 6 nodes and 8 edges

Note that the resulting graph object reports a single time step ``t=1``, as it has not yet been
`sliced <#slice-temporal-graph>`__.

.. attention::

   To allow multiple interactions between the same nodes over time, a
   :class:`~networkx_temporal.classes.TemporalMultiGraph` or
   :class:`~networkx_temporal.classes.TemporalMultiDiGraph` object is required. Otherwise, only a
   single edge is allowed among pairs.


Import static graphs
====================

Static graph objects with temporal information may also be imported as temporal graphs.

.. code-block:: python

   >>> G = nx.DiGraph()
   >>>
   >>> G.add_nodes_from([
   >>>     ("a", {"time": 0}),
   >>>     ("b", {"time": 0}),
   >>>     ("c", {"time": 1}),
   >>>     ("d", {"time": 2}),
   >>>     ("e", {"time": 3}),
   >>>     ("f", {"time": 3}),
   >>> ])
   >>>
   >>> G.add_edges_from([
   >>>     ("a", "b", {"time": 0}),
   >>>     ("c", "b", {"time": 1}),
   >>>     ("d", "c", {"time": 2}),
   >>>     ("d", "e", {"time": 2}),
   >>>     ("a", "c", {"time": 2}),
   >>>     ("f", "e", {"time": 3}),
   >>>     ("f", "a", {"time": 3}),
   >>>     ("f", "b", {"time": 3}),
   >>> ])
   >>>
   >>> print(G)

   DiGraph with 6 nodes and 8 edges

We may convert the graph above to a :class:`~networkx_temporal.classes.TemporalGraph` object
using the :func:`~networkx_temporal.transform.from_static` function.
As expected, the resulting object has the same total number of nodes and edges as the original graph:

.. code-block:: python

   >>> TG = tx.from_static(G)
   >>>
   >>> # assert G.order() == TG.order(copies=False)
   >>> # assert G.size() == TG.size(copies=True)
   >>>
   >>> print(TG)

   TemporalDiGraph (t=1) with 6 nodes and 8 edges

The :func:`~networkx_temporal.drawing.draw` function allows to visualize the edge-level temporal
information in a single plot:

.. code-block:: python

   >>> tx.draw(TG, layout="kamada_kawai", edge_labels="time", suptitle="Temporal Graph")

.. image:: ../../assets/figure/fig-4.png
   :align: center

However, note that in the example above, both the nodes and edges contain a ``time`` attribute.
Let's see next how this affects the resulting temporal graph when slicing the graph data into snapshots.

.. seealso::

   The :func:`~networkx_temporal.transform.from_snapshots` function to import a list of static graphs as
   temporal graph snapshots.


Slice temporal graph
====================

Let's use the :func:`~networkx_temporal.classes.TemporalGraph.slice` method to split the temporal graph we
created into a number of snapshots:

.. code-block:: python

   >>> TG = TG.slice(attr="time")
   >>> print(TG)

   TemporalDiGraph (t=4) with 6 nodes and 8 edges

Inspecting the resulting object's properties can be achieved using some familiar methods:

.. code-block:: python

   >>> print(f"t = {len(TG)} time steps\n"
   ...       f"V = {TG.order()} nodes "
   ...       f"({TG.order(copies=False)} unique, {TG.order(copies=True)} total)\n"
   ...       f"E = {TG.size()} edges "
   ...       f"({TG.size(copies=False)} unique, {TG.size(copies=True)} total)")

   t = 4 time steps
   V = [2, 2, 4, 4] nodes (6 unique, 12 total)
   E = [1, 1, 3, 3] edges (8 unique, 8 total)

We may also visualize the resulting snapshots using the :func:`~networkx_temporal.drawing.draw` function:

.. code-block:: python

   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../assets/figure/fig-0.png
   :align: center

Note that :func:`~networkx_temporal.classes.TemporalGraph.slice` by default returns a snapshot for each
unique attribute value in the graph.

.. hint::

   By default, :func:`~networkx_temporal.classes.TemporalGraph.slice`
   returns the interval of the resulting
   snapshots as their :attr:`~networkx_temporal.classes.TemporalGraph.names`
   property. Passing ``title=True`` to :func:`~networkx_temporal.drawing.draw`
   will use them instead of indices as subplot titles, as seen below.


Number of snapshots
--------------------

A new object can be created with a specific number of snapshots by setting the
``bins`` parameter:

.. code-block:: python

   >>> TG = TG.slice(attr="time", bins=2)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2), names=True)

.. image:: ../../assets/figure/fig-1.png
   :align: center

.. note::

   In case :func:`~networkx_temporal.classes.TemporalGraph.slice`
   is not able to split the graph into the number of snapshots
   specified by ``bins`` (e.g., due to insufficient data), the maximum
   possible number of snapshots is returned instead.


Quantile-based cut
------------------

Setting ``qcut=True`` slices a graph into quantiles, creating snapshots with balanced order and/or
size (nodes/edges). This is useful when interactions are not evenly distributed across time.
For example:

.. code-block:: python

   >>> TG = TG.slice(attr="time", bins=2, qcut=True)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2), names=True)

.. image:: ../../assets/figure/fig-2.png
   :align: center

The resulting snapshots have uneven time intervals: :math:`t=(0,2]` and :math:`t=(2,3]`, respectively.
Objects are sorted by their ``time`` attribute values and then split into two groups with approximately
the same order (nodes) or size (edges), depending on the level of the attribute passed to the function.

.. seealso::

   The `pandas.qcut documentation
   <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.qcut.html>`__
   for more information on quantile-based discretization.


Rank-based cut
--------------

Setting ``rank_first=True`` slices a graph considering the order of appearance of edges (default),
nodes, or attributes, forcing each snapshot to have approximately the same number of objects:

.. code-block:: python

   >>> TG = TG.slice(bins=2, rank_first=True)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2), names=True)

.. image:: ../../assets/figure/fig-3.png
   :align: center

As ``attr`` was not set, the graph was split considering the order in which edges were added
to the graph. Notice how each snapshot title now refer to edge intervals: :math:`e_0` to :math:`e_3`
:math:`(0, 4]` and :math:`e_4` to :math:`e_7` :math:`(4, 8]`.
This is useful to obtain an arbitrary number of subgraphs, independent of their temporal dynamics.

.. seealso::

   The `pandas.rank documentation
   <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.rank.html>`__
   for more information on ranking data.


Edge-level time attribute
-------------------------

Converting a static graph considering edge-level temporal data into a temporal graph object:

.. code-block:: python

   >>> TG = TG.slice(attr="time")  # level="edge"
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../assets/figure/fig-5.png
   :align: center

The resulting temporal graph has the same number of edges as the original graph, but a higher number
of nodes. This is expected, as the same nodes appear in more than one snapshot.

.. note::

   By default, :func:`~networkx_temporal.classes.TemporalGraph.slice` considers ``attr`` as an edge-level
   attribute, which is usually the case for temporal data. This behavior can be changed by setting
   ``level='node'``, as seen below.


Node-level time attribute
-------------------------

Converting a static graph considering node-level temporal data to a temporal graph object:

.. code-block:: python

   >>> TG = TG.slice(attr="time", level="node")
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../assets/figure/fig-6.png
   :align: center

Note that now, even though the edge :math:`(a, c)` contains the attribute ``time=2``, the
performed node-level slice resulted in it being placed at the snapshot :math:`t=0` instead, as node
:math:`a` is set to ``time=0``:

.. code-block:: python

   >>> G.nodes(data="time")["a"]

   0

.. note::

    When ``level='node'``, the source node's ``attr`` value is used by default to determine the
    edge's interaction time. This behavior can be changed by setting ``level='target'`` instead.


Save and load data
==================

Temporal graphs may be read from or written to a file using
:func:`~networkx_temporal.readwrite.read_graph` and :func:`~networkx_temporal.readwrite.write_graph`:

.. code-block:: python

   >>> tx.write_graph(TG, "temporal-graph.graphml.zip")
   >>> TG = tx.read_graph("temporal-graph.graphml.zip")

Supported formats are the same as those in NetworkX and depend on the version installed.

.. seealso::

   The `read and write documentation
   <https://networkx.org/documentation/stable/reference/io/index.html>`__
   from NetworkX for a list of supported graph formats.


Inherited methods
=================

Any methods available from a `NetworkX graph
<https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph>`__
can be called directly from a :class:`~networkx_temporal.classes.TemporalGraph` object.
For example, the familiar methods below transform edges in the graph into directed or undirected:

.. code-block:: python

   >>> TG.to_undirected()

   <networkx_temporal.classes.graph.TemporalGraph at 0x7f13dcde4dd0>

.. code-block:: python

   >>> TG.to_directed()

   <networkx_temporal.classes.digraph.TemporalDiGraph at 0x7f13dcdccdd0>

Note that both methods return new objects when called, so the original graph remains unchanged.
Additional utility functions for temporal graphs are available in the
:mod:`~networkx_temporal.utils` module.

.. seealso::

   - The `Appendix → Index <../genindex.html>`__  page for a list of the implemented classes,
     methods, and functions.

   - The `NetworkX documentation
     <https://networkx.org/documentation/stable/reference/classes/graph.html#methods>`__
     for a list of methods inherited by a :class:`~networkx_temporal.classes.TemporalGraph`
     object.
