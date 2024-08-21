.. hint::

    This guide is also available as an interactive
    `Jupyter notebook
    <https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__
    (`open on Colab
    <https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__).


################
Basic operations
################

The examples below cover the package's basic functionalities, including how to build a temporal
graph, slice it into snapshots, and save and load the resulting objects to disk.


Build temporal graph
====================

The main class of the package is the
:class:`~networkx_temporal.TemporalGraph`
object, which extends `NetworkX's graphs
<https://networkx.org/documentation/stable/reference/classes/index.html>`__
to handle temporal data.
Let's start by creating a simple directed graph using ``time`` as attribute key:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalGraph(directed=True)
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

.. note::

   Multigraphs are particularly useful to represent temporal graphs, as it allows to store multiple
   interactions between the same nodes at different time steps within a single graph object. This
   behavior can be changed by setting ``multigraph=False`` when creating the :class:`~networkx_temporal.TemporalGraph` object.


From a static graph
-------------------

Static graphs may too carry temporal information in both node- and edge-level attributes.

Slicing a graph into bins usually result in the same number of edges, but a higher number of nodes,
as they may appear in more than one snapshot. In the example below, we create a static multigraph in
which both nodes and edges are attributed with the time step in which they are observed:

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


Edge-level time attribute
^^^^^^^^^^^^^^^^^^^^^^^^^

Converting a static graph with edge-level temporal data to a temporal graph object:

.. code-block:: python

   >>> TG = tx.from_static(G).slice(attr="time")
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../figure/fig-5.png

The resulting temporal graph has the same number of edges as the original graph, but a higher number
of nodes. This is expected, as the same nodes appear in more than one snapshot.

.. note::

   By default, :func:`~networkx_temporal.TemporalGraph.slice` considers ``attr`` as an edge-level attribute, which is usually the case for
   temporal data. This behavior can be changed by setting ``attr_level='node'`` (see example below).


Node-level time attribute
^^^^^^^^^^^^^^^^^^^^^^^^^

Converting a static graph with node-level temporal data to a temporal graph object:

.. code-block:: python

   >>> TG = tx.from_static(G).slice(attr="time", attr_level="node")
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../figure/fig-4.png

Note that even though the edge :math:`(a, c)` contains the attribute ``time=2``, considering
node-level attributes resulted in it being placed at :math:`t=0` instead, as the source node
:math:`a` is set to ``time=0``:

.. code-block:: python

   >>> G.nodes(data="time")["a"]

   0

.. note::

    By default, the source node's temporal attribute is used to determine the time step of an edge
    with ``attr_level='node'``. This behavior can be changed by setting ``node_level='target'`` instead.


-----

Slice temporal graph
====================

Let's use the :func:`~networkx_temporal.TemporalGraph.slice` method to split the temporal graph we created into a number of snapshots:

.. code-block:: python

   >>> TG = TG.slice(attr="time")
   >>> TG

   TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges

Inspecting the resulting object's properties can be achieved with some familiar methods:

.. code-block:: python

   >>> print(f"t = {len(TG)} time steps\n"
   >>>       f"V = {TG.order()} nodes ({TG.temporal_order()} unique, {TG.total_nodes()} total)\n"
   >>>       f"E = {TG.size()} edges ({TG.temporal_size()} unique, {TG.total_edges()} total)")

   t = 4 time steps
   V = [2, 2, 4, 4] nodes (6 unique, 12 total)
   E = [1, 1, 3, 3] edges (8 unique, 8 total)


We may now visualize the resulting snapshots using the :func:`~networkx_temporal.draw` function:

.. code-block:: python

   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: ../../figure/fig-0.png

Specifying number of snapshots
------------------------------

A new object can be created with a specific number of snapshots by setting the
``bins`` parameter:

.. code-block:: python

   >>> TG = TG.slice(attr="time", bins=2)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2))

.. image:: ../../figure/fig-1.png

Note that this usually leads to snapshots with differing numbers of nodes and edges, as expected.

Considering quantiles
---------------------

By default, created bins are composed of non-overlapping edges and might have uneven order and/or
size. To try and balance them using quantiles, pass ``qcut=True`` (see `pandas.qcut
<https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.qcut.html>`__ for details):

.. code-block:: python

   >>> TG = TG.slice(attr="time", bins=2, qcut=True)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2))

.. image:: ../../figure/fig-2.png

Though not perfectly balanced due to node :math:`a` appearing multiple times (in :math:`t={1,2,3}`),
the resulting snapshots have a more even number of edges. Results are expected to vary in a
case-by-case basis.

Ranking nodes or edges
----------------------

Forcing a number of bins can be achieved by setting ``rank_first=True``, ranking nodes or edges by
their order of appearance in the original graph (see `pandas.Series.rank
<https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.rank.html>`__ for details):

.. code-block:: python

   >>> TG = TG.slice(attr="time", bins=2, rank_first=True)
   >>> tx.draw(TG, layout="kamada_kawai", figsize=(4, 2))

.. image:: ../../figure/fig-3.png

As the `time` attribute is here located in the edge level, each resulting snapshot has 4 edges each.
In case of node-level times, the number of nodes in each snapshot would be more evenly distributed.

.. note::
   In some cases, it may still not be able to split the graph into the number of snapshots specified
   by ``bins`` (e.g., due to insufficient data). The maximum possible number is returned instead.


-----

Save and load data
==================

Temporal graphs may be read from or written to a file using the following functions:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.read_graph("path/to/file.ext")
   >>> tx.write_graph("path/to/file.ext")  # or TG.write_graph("path/to/file.ext")

Supported formats will be automatically detected based on the file extension.
For details on the methods, please refer to their respective documentation:
:func:`~networkx_temporal.read_graph` and :func:`~networkx_temporal.write_graph`.

.. seealso::

   The `read and write documentation
   <https://networkx.org/documentation/stable/reference/readwrite/index.html>`__
   from NetworkX for a list of supported graph formats.


-----

Edge direction
==============

Similar to static NetworkX graphs, edges in a temporal graph can be easily transformed into directed
or undirected by calling the :func:`~networkx_temporal.to_directed` or :func:`~networkx_temporal.to_undirected` methods, respectively:

.. code-block:: python

   >>> TG.to_undirected()

   TemporalGraph (t=4) with 12 nodes and 8 edges

.. code-block:: python

   >>> TG.to_directed()

   TemporalDiGraph (t=4) with 12 nodes and 16 edges

As the methods return new objects, the original graph remains unchanged. Note that most methods
available in the `NetworkX graphs <https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph>`__
can be called directly from the :class:`~networkx_temporal.TemporalGraph` object as well.
