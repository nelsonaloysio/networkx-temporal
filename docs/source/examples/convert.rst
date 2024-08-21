.. hint::

    This guide is also available as an interactive
    `Jupyter notebook
    <https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__
    (`open on Colab
    <https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__).


#####################
Convert and transform
#####################

The package provides a set of functions to convert to different graph formats and representations.
In this context, ''converting'' refers to changing the underlying graph object type, e.g.
`igraph <https://igraph.org>`__.
while ''transforming'' refers to changing the graph representation, e.g.,
`event-based temporal graphs <#event-based-temporal-graph>`__.

.. note::

   Contributions are welcome! If you would like to see a specific graph format or representation
   implemented, please feel free to submit a pull request on the package's `GitHub repository
   <https://github.com/nelsonaloysio/networkx-temporal>`__.


Graph formats
=============

Graphs may be converted to a different object type by calling :func:`~networkx_temporal.convert`
with the desired format:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalGraph(directed=True, multigraph=False)
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
   >>> tx.convert(TG.to_static(), "igraph")

   <igraph.Graph at 0x7f048ef52c50>

In the example above, the temporal graph ``TG`` is first flattened using :func:`~to_static`.
Instead, temporal graphs will return a list of objects, one per snapshot
post-:func:`~slice`, as shown below:

.. code-block:: python

   >>> TG = TG.slice(attr="time")
   >>>
   >>> tx.convert(TG, "igraph")

   [<igraph.Graph at 0x7f048ef52450>,
    <igraph.Graph at 0x7f048ef52950>,
    <igraph.Graph at 0x7f048ef52a50>,
    <igraph.Graph at 0x7f048ef52b50>]

Support for the following output formats are implemented, here listed with their respective aliases:

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


-----

Graph representations
=====================

Once a temporal graph is instantiated, the following methods allow returning static graphs,
snapshots events or unified representations.  Due to the way the underlying data is represented,
some of these objects (i.e., those with unique nodes) do not allow dynamic node attributes.

Observe that the total number of nodes :math:`V` and edges :math:`E` of the returned object might
differ from the number of temporal nodes :math:`V_T` and edges :math:`E_T`, depending on the data
and method used:

+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| Method           | .. centered :: Order | .. centered :: Size | Dynamic node attributes            | Dynamic edge attributes             |
+==================+======================+=====================+====================================+=====================================+
| ``to_static``    | :math:`V = V_T`      | :math:`E = E_T`     | .. centered:: |:x:|                | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| ``to_snapshots`` | :math:`V \ge V_T`    | :math:`E = E_T`     | .. centered:: |:heavy_check_mark:| | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| ``to_events``    | :math:`V = V_T`      | :math:`E = E_T`     | .. centered:: |:x:|                | .. centered:: |:x:|                 |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+
| ``to_unified``   | :math:`V \ge V_T`    | :math:`E \ge E_T`   | .. centered:: |:heavy_check_mark:| | .. centered:: |:heavy_check_mark:|  |
+------------------+----------------------+---------------------+------------------------------------+-------------------------------------+


Static graph
------------

Builds a static or flattened graph ``G`` containing all the edges found at each time step.

.. important::

   Dynamic node attributes in a temporal graph are not preserved in a static graph.


.. rubric:: TemporalGraph → G

.. code-block:: python

    >>> G = TG.to_static()
    >>> G

    MultiDiGraph with 6 nodes and 8 edges

.. code-block:: python

   >>> tx.draw(G, layout="kamada_kawai", suptitle="Static Graph")

.. image:: ../../figure/fig_44.png

.. rubric:: G → TemporalGraph

.. code-block:: python

    >>> TG = tx.from_static(G).slice(attr="time")
    >>> print(TG)

    TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges


Snapshot-based temporal graph
-----------------------------

A snapshot-based temporal graph ``STG`` is a sequence of graphs where each element represents a
snapshot of the original temporal graph. It is the most common representation of temporal graphs.

.. note::

   Like the :func:`~networkx_temporal.TemporalGraph.slice` method, this function internally returns
   views of the original graph data, so no data is copied unless specified otherwise, i.e., by
   passing ``as_view=False`` to the function.

.. rubric:: TemporalGraph → STG

.. code-block:: python

   >>> STG = TG.to_snapshots()
   >>> STG

   [<networkx.classes.graph.Graph at 0x7fd9132420d0>,
    <networkx.classes.graph.Graph at 0x7fd913193710>,
    <networkx.classes.graph.Graph at 0x7fd912906d50>,
    <networkx.classes.graph.Graph at 0x7fd91290d350>]

.. rubric:: STG → TemporalGraph

.. code-block:: python

   >>> TG = tx.from_snapshots(STG)
   >>> TG

    TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges


Event-based temporal graph
--------------------------

An event-based temporal graph ``ETG`` is a sequence of 3- or 4-tuple edge-based events.

* **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time attribute;

* **4-tuples** (:math:`u, v, t, \epsilon`), where an additional element :math:`\epsilon` is either a
  positive (``1``) or negative (``-1``) unity representing edge addition and deletion events, respectively.

Depending on the temporal graph data, one of these may allow a more compact representation than the
other. The default is to return a 3-tuple sequence (also known as a *stream graph*).

.. important::

   Event-based temporal graphs do not currently store node- or edge-level attribute data.
   Moreover, as sequences of events are edge-based, node isolates are not preserved.

.. rubric:: TemporalGraph → ETG

.. code-block:: python

   >>> ETG = TG.to_events()  # stream=True (default)
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

   >>> ETG = TG.to_events(stream=False)
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

.. rubric:: ETG → TemporalGraph

.. code-block:: python

   >>> tx.from_events(ETG, directed=True, multigraph=True)

   TemporalDiGraph (t=4) with 12 nodes and 8 edges


Unified temporal graph
----------------------

A unified temporal graph ``UTG`` is a single graph object that contains the original temporal data,
plus ''proxy'' nodes (*from each snapshot*) and edge ''couplings'' (*linking sequential temporal
nodes*). Its usefulness is restricted to certain types of analysis and visualization, e.g., based on
temporal flows.

.. rubric:: TemporalGraph → UTG

.. code-block:: python

   >>> UTG = TG.to_unified(add_couplings=True)
   >>> print(UTG)

   MultiDiGraph named 'UTG (t=4, proxy_nodes=6, edge_couplings=2)' with 12 nodes and 14 edges

.. code-block:: python

   >>> nodes = sorted(TG.temporal_nodes())
   >>>
   >>> pos = {node: (nodes.index(node.rsplit("_")[0]), -int(node.rsplit("_")[1]))
   >>>        for node in UTG.nodes()}
   >>>
   >>> tx.draw(UTG,
               pos=pos,
               figsize=(4, 4),
               connectionstyle="arc3,rad=0.25",
               suptitle="Unified Temporal Graph")

.. image:: ../../figure/fig_52.png

.. rubric:: UTG → TemporalGraph

.. code-block:: python

   >>> tx.from_unified(UTG)

   TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges
