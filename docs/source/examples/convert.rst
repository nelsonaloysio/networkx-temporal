.. include:: ../include-examples.rst

#####################
Convert and transform
#####################

This package provides a set of functions to manipulate graph classes, formats, and representations.
In this context, :mod:`~networkx_temporal.utils.convert` refers to different graph-based libraries,
e.g., `igraph <https://igraph.org/python>`__, and :mod:`~networkx_temporal.transform` refers to the
underlying data structure used to store object relations, e.g.,
`event-based temporal graphs <#event-based-temporal-graph>`__.

.. note::

   Contributions are welcome! If you would like to see a specific graph format or representation
   implemented, please feel free to submit a pull request on the package's `GitHub repository
   <https://github.com/nelsonaloysio/networkx-temporal>`__.


Graph classes
=============

Static or temporal multigraphs may be converted to graphs without parallel edges and vice-versa:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalMultiDiGraph()  # TG = tx.temporal_graph(directed=True, multigraph=True)
   >>>
   >>> TG.add_edge("a", "b", time=0)
   >>> TG.add_edge("c", "b", time=0)
   >>> TG.add_edge("c", "b", time=1)   # parallel edge
   >>> TG.add_edge("d", "c", time=2)
   >>> TG.add_edge("d", "e", time=2)
   >>> TG.add_edge("a", "c", time=2)
   >>> TG.add_edge("f", "e", time=3)
   >>> TG.add_edge("f", "a", time=3)
   >>> TG.add_edge("f", "b", time=3)
   >>>
   >>> TG = TG.slice(attr="time")
   >>> print(TG)

   TemporalMultiDiGraph (t=4) with 6 nodes and 9 edges


In the example above, the temporal multigraph ``TG`` was first sliced into :math:`t=4` snapshots.
Let's now convert it to a simple graph, in which parallel edges among the same node pair are
not allowed:

.. code-block:: python

   >>> TG = tx.from_multigraph(TG)
   >>> print(TG)

   TemporalDiGraph (t=4) with 6 nodes and 9 edges

The resulting graph has the same size of :math:`|\mathcal{E}| = 9` edges, as the parallel edges
among nodes :math:`c` and :math:`b` were in different snapshots, :math:`t=\{0,1\}`.
Let's now :func:`~networkx_temporal.graph.TemporalGraph.flatten` it and call
:func:`~networkx_temporal.utils.from_multigraph` again:

.. code-block:: python

   >>> TG = tx.to_multigraph(TG)    # Restore temporal graph back to a multigraph.
   >>> TG = TG.flatten()            # Obtain temporal graph with a single snapshot.
   >>> TG = tx.from_multigraph(TG)  # Combine parallel edges into single ones.
   >>>
   >>> print(TG)
   >>> TG.edges(("c", "b"), data=True)

   TemporalDiGraph (t=4) with 6 nodes and 8 edges
   [OutEdgeDataView([('c', 'b', {'time': 1, 'weight': 2})])]

In this case, the resulting graph has :math:`|\mathcal{E}| = 8` edges, as the parallel edges
among nodes :math:`c` and :math:`b` were combined into a single one with the attributes
``time=1`` and ``weight=2``, referring to the last snapshot time and their total number of
interactions, respectively, resulting in an irreversible operation.

.. attention::

   The conversion from a temporal multigraph to a simple graph is not always reversible, and
   dynamic edge attributes, e.g., ``time``, are overwritten when converting multigraphs to graphs.


Graph formats
=============

Graphs may also be converted to a different format by passing the desired library to
:func:`~networkx_temporal.utils.convert.convert`:

.. code-block:: python

   >>> tx.convert(TG.to_static(), "igraph")

   <igraph.Graph at 0x7ff6f1803d40>

In the example above, the temporal graph ``TG`` was first transformed into a `static graph
<#static-graph>`__, which is not required. By default, the function returns a list of graph
objects, one per snapshot, as shown below:

.. code-block:: python

   >>> tx.convert(TG, "igraph")

   [<igraph.Graph at 0x7ff6f1803e40>,
    <igraph.Graph at 0x7ff6f181c040>,
    <igraph.Graph at 0x7ff6f181c140>,
    <igraph.Graph at 0x7ff6f181c240>]

Support for the following libraries are currently implemented by the package:

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


-----

Graph representations
=====================

Once instantiated, :class:`~networkx_temporal.graph.TemporalGraph` objects may be transformed into
different representations, depending on the analysis or visualization requirements. Due to the
nature of temporal graphs, some representations may not preserve all the data, such as dynamic node
or edge attributes.

Observe that the total number of returned nodes :math:`V` and edges :math:`E`
after transformation might differ from the number of temporal nodes :math:`V_T` and
edges :math:`E_T`, depending on the data and method used:

+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| Representation   | .. centered:: Order  | .. centered:: Size  | Dynamic node attributes            | Dynamic edge attributes             |
+==================+======================+=====================+====================================+=====================================+
| |to_static|_     | :math:`V = V_T`      | :math:`E = E_T`     | .. centered:: |:x:|                | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| |to_snapshots|_  | :math:`V \ge V_T`    | :math:`E = E_T`     | .. centered:: |:heavy_check_mark:| | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| |to_events|_     | :math:`V = V_T`      | :math:`E = E_T`     | .. centered:: |:x:|                | .. centered:: |:x:|                 |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| |to_unified|_    | :math:`V \ge V_T`    | :math:`E \ge E_T`   | .. centered:: |:heavy_check_mark:| | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+

.. .. |to_static| replace:: :func:`~networkx_temporal.graph.TemporalGraph.to_static`
.. .. |to_snapshots| replace:: :func:`~networkx_temporal.graph.TemporalGraph.to_snapshots`
.. .. |to_events| replace:: :func:`~networkx_temporal.graph.TemporalGraph.to_events`
.. .. |to_unified| replace:: :func:`~networkx_temporal.graph.TemporalGraph.to_unified`

.. |to_static| replace:: Static
.. _to_static: #static-graph

.. |to_snapshots| replace:: Snapshots\*
.. _to_snapshots: #snapshot-based-temporal-graph

.. |to_events| replace:: Events
.. _to_events: #event-based-temporal-graph

.. |to_unified| replace:: Unified
.. _to_unified: #unified-temporal-graph

(\*) Default underlying data structure for temporal graphs with multiple snapshots on
:func:`~networkx_temporal.graph.TemporalGraph.slice`.


Static graph
------------

A static graph :const:`G` is a single graph object containing all the nodes and edges found in the
temporal graph. It is the simplest representation of a network and is the most common type of graph.

.. attention::

   Dynamic node attributes are not preserved when transforming a temporal to a static graph.

.. seealso::

   The `Basic operations → Import static graphs <basics.html#import-static-graphs>`__ page for
   more static graph conversion examples.


:const:`TG` → :const:`G`
^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a :class:`~networkx_temporal.graph.TemporalGraph` into a static graph
with the :func:`~networkx_temporal.graph.TemporalGraph.to_static` method:

.. code-block:: python

   >>> G = TG.to_static()
   >>> print(G)

    DiGraph with 6 nodes and 8 edges

.. code-block:: python

   >>> tx.draw(G, layout="kamada_kawai", suptitle="Static Graph")

.. image:: ../../assets/figure/fig-7.png


:const:`G` → :const:`TG`
^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a static graph into a :class:`~networkx_temporal.graph.TemporalGraph`
with the :func:`~networkx_temporal.transform.from_static` function:

.. code-block:: python

   >>> TG = tx.from_static(G)
   >>> TG = TG.slice(attr="time")
   >>> print(TG)

   TemporalDiGraph (t=1) with 6 nodes and 8 edges


Snapshot-based temporal graph
-----------------------------

A snapshot-based temporal graph :const:`STG` is a sequence of graphs where each element represents a
snapshot of the original temporal graph. It is the most common representation of temporal graphs.

.. note::

   Like the :func:`~networkx_temporal.graph.TemporalGraph.slice` method,
   :func:`~networkx_temporal.graph.TemporalGraph.to_snapshots` internally returns
   views of the original graph data, so no data is copied unless specified otherwise, i.e., by
   passing ``as_view=False`` to the function.


:const:`TG` → :const:`STG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a :class:`~networkx_temporal.graph.TemporalGraph` into a snapshot-based
temporal graph with :func:`~networkx_temporal.graph.TemporalGraph.to_snapshots`:

.. code-block:: python

   >>> STG = TG.to_snapshots()
   >>> STG

   [<networkx.classes.graph.Graph at 0x7fd9132420d0>,
    <networkx.classes.graph.Graph at 0x7fd913193710>,
    <networkx.classes.graph.Graph at 0x7fd912906d50>,
    <networkx.classes.graph.Graph at 0x7fd91290d350>]


:const:`STG` → :const:`TG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a snapshot-based temporal graph into a :class:`~networkx_temporal.graph.TemporalGraph` with
:func:`~networkx_temporal.transform.from_snapshots`:

.. code-block:: python

   >>> TG = tx.from_snapshots(STG)
   >>> print(TG)

   TemporalDiGraph (t=4) with 6 nodes and 8 edges


Event-based temporal graph
--------------------------

An event-based temporal graph :const:`ETG` is a sequence of 3- or 4-tuple edge-based events.

* **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time attribute;

* **4-tuples** (:math:`u, v, t, \varepsilon`), where an additional element :math:`\varepsilon` is either an
  ``int`` for edge addition (``1``) or deletion (``-1``) events, or a ``float`` for the duration
  of the interaction (zero for a single snapshot).

Depending on the temporal graph data, one of these may allow a more compact representation than the
others. The default is to return a 3-tuple sequence (also known as a *stream graph*).

.. attention::

   As events are edge-based, node isolates without self-loops are not preserved.


:const:`TG` → :const:`ETG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a :class:`~networkx_temporal.graph.TemporalGraph` into an event-based temporal
graph with :func:`~networkx_temporal.graph.TemporalGraph.to_events`:

.. code-block:: python

   >>> ETG = TG.to_events()  # eps=None
   >>> ETG

   [('a', 'b', 0),
    ('c', 'b', 1),
    ('a', 'c', 2),
    ('d', 'c', 2),
    ('d', 'e', 2),
    ('f', 'e', 3),
    ('f', 'a', 3),
    ('f', 'b', 3)]

.. code-block:: python

   >>> ETG = TG.to_events(eps=int)
   >>> ETG

   [('a', 'b', 0, 1),
    ('c', 'b', 1, 1),
    ('a', 'b', 1, -1),
    ('a', 'c', 2, 1),
    ('d', 'c', 2, 1),
    ('d', 'e', 2, 1),
    ('c', 'b', 2, -1),
    ('f', 'e', 3, 1),
    ('f', 'a', 3, 1),
    ('f', 'b', 3, 1),
    ('a', 'c', 3, -1),
    ('d', 'c', 3, -1),
    ('d', 'e', 3, -1)]

.. code-block:: python

   >>> ETG = TG.to_events(eps=float)
   >>> ETG

   [('a', 'b', 0, 0.0),
    ('c', 'b', 1, 0.0),
    ('a', 'c', 2, 0.0),
    ('d', 'c', 2, 0.0),
    ('d', 'e', 2, 0.0),
    ('f', 'e', 3, 0.0),
    ('f', 'a', 3, 0.0),
    ('f', 'b', 3, 0.0)]


:const:`ETG` → :const:`TG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming an event-based temporal graph into a :class:`~networkx_temporal.graph.TemporalGraph` with
:func:`~networkx_temporal.transform.from_events`:

.. code-block:: python

   >>> TG = tx.from_events(ETG, directed=True, multigraph=True)
   >>> print(TG)

   TemporalDiGraph (t=4) with 6 nodes and 8 edges


Unified temporal graph
----------------------

A unified temporal graph :const:`UTG` is a single graph object that contains the original temporal data,
plus additional time-adjacent node copies (from each snapshot) and edge couplings connecting them.
Its usefulness is restricted to certain types of analysis and visualization, e.g., based on
temporal flows.


:const:`TG` → :const:`UTG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a :class:`~networkx_temporal.graph.TemporalGraph` into a unified temporal
graph with :func:`~networkx_temporal.graph.TemporalGraph.to_unified`:

.. code-block:: python

   >>> UTG = TG.to_unified(add_couplings=True)
   >>> print(UTG)

   MultiDiGraph named 'UTG (t=4, proxy_nodes=6, edge_couplings=6)' with 6 nodes and 14 edges

Let's draw the resulting graph to visualize the node copies (in black) and edge couplings (dotted):

.. code-block:: python

   >>> c0, c1 = "tab:red", "#333"
   >>>
   >>> nodes = sorted(TG.temporal_nodes())
   >>>
   >>> pos = {n: (int(n.rsplit("_")[1]), -nodes.index(n.rsplit("_")[0]))
   >>>        for n in UTG.nodes()}
   >>>
   >>> labels = {n: f"{n.split('_')[0]}$_{n.split('_')[1]}$"
   >>>           for n in UTG.nodes()}
   >>>
   >>> node_color = [c1 if int(n.split("_")[1]) != TG.index_node(n.split("_")[0])[0] else c0
   >>>               for n in UTG.nodes()]
   >>>
   >>> edge_style = ["dotted" if u.split("_")[0] == v.split("_")[0] else "solid"
   >>>               for u, v in UTG.edges()]
   >>>
   >>> tx.draw(
   >>>     UTG,
   >>>     pos=pos,
   >>>     figsize=(4.5, 4.5),
   >>>     labels=labels,
   >>>     node_size=450,
   >>>     node_color=node_color,
   >>>     style=edge_style,
   >>>     width=1.5,
   >>>     connectionstyle="arc3,rad=0.25",
   >>>     suptitle="Unified Temporal Graph")

.. image:: ../../assets/figure/fig-8.png


:const:`UTG` → :const:`TG`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Transforming a unified temporal graph into a :class:`~networkx_temporal.graph.TemporalGraph` with
:func:`~networkx_temporal.transform.from_unified`:

.. code-block:: python

   >>> TG = tx.from_unified(UTG)
   >>> print(TG)

   TemporalMultiDiGraph (t=4) with 6 nodes and 8 edges
