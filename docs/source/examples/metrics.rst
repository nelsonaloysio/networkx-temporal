.. include:: ../include/notebook.rst

##############
Common metrics
##############

This section showcases some common metrics available for temporal graphs and its snapshots, that is,
the individual (static) graphs that compose a :class:`~networkx_temporal.TemporalGraph` object after calling :func:`~networkx_temporal.TemporalGraph.slice`.

.. note::

   Contributions are welcome! If you would like to see a specific metric for temporal graphs
   implemented, please feel free to submit a pull request on the package's `GitHub repository
   <https://github.com/nelsonaloysio/networkx-temporal>`__.


Static graph metrics
====================

The functions and algorithms implemented by NetworkX can be applied directly on the temporal graph
snapshots, either by iterating over them or by calling the `corresponding methods
<https://networkx.org/documentation/stable/reference/classes/graph.html#methods>`__ directly.

Such methods are executed on each graph snapshot when called and return a list of results --- unless
in case of specific functions that have been overriden, maintaining their use, such as :func:`~networkx_temporal.is_directed`.



Degree centrality
-----------------

Methods such as
`degree <https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.degree.html>`__,
`in_degree <https://networkx.org/documentation/stable/reference/classes/generated/networkx.DiGraph.in_degree.html>`__, and
`out_degree <https://networkx.org/documentation/stable/reference/classes/generated/networkx.DiGraph.out_degree.html>`__
return a list of degree views per snapshot:

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
   >>> TG = TG.slice(attr="time")
   >>>
   >>> TG.degree()

   [DiMultiDegreeView({'b': 1, 'a': 1}),
    DiMultiDegreeView({'b': 1, 'c': 1}),
    DiMultiDegreeView({'a': 1, 'c': 2, 'd': 2, 'e': 1}),
    DiMultiDegreeView({'a': 1, 'b': 1, 'e': 1, 'f': 3})]

Alternatively, we may obtain the degree of a specific node in a given snapshot, e.g., node :math:`a_0`:

.. code-block:: python

   >>> TG[0].degree("a")

   1


Order and size
--------------

Similarly, to obtain the total number of nodes and edges in each snapshot:

.. code-block:: python

   >>> print("Order:", TG.order())
   >>> print("Size:", TG.size())

   Order: [2, 2, 4, 4]
   Size: [1, 1, 3, 3]


Node neighborhoods
------------------

The ``neighbors`` method returns a list of neighbors for each node in each snapshot:

.. code-block:: python

   >>> TG.neighbors("c")

   [[], ['b'], [], []]

Converting the graph to undirected, we also obtain nodes that have node :math:`c` as their neighbor:

.. code-block:: python

   >>> TG.to_undirected().temporal_neighbors("c")

   [[], ['b'], ['a', 'd'], []]


-----

Temporal graph metrics
======================

Only a few methods that consider all snapshots are currently available from :class:`~networkx_temporal.TemporalGraph` objects.
They mostly serve as wrappers of the available functions in NetworkX, for convenience purposes.


Temporal degree centrality
--------------------------

Meanwhile, :func:`~networkx_temporal.TemporalGraph.temporal_degree` returns a dictionary containing node degrees across all time steps:

.. code-block:: python

   >>> TG.temporal_degree()

   {'e': 4, 'b': 6, 'f': 6, 'a': 6, 'd': 4, 'c': 6}

Alternatively, to obtain the degree of a specific node considering all snapshots, e.g., node :math:`a`:

.. code-block:: python

   >>> TG.temporal_degree("a")

   6


Temporal order and size
-----------------------

The :func:`~networkx_temporal.TemporalGraph.temporal_order` and :func:`~networkx_temporal.TemporalGraph.temporal_size` functions
return the number of unique nodes and edges:

.. code-block:: python

   >>> print("Temporal nodes:", TG.temporal_order())
   >>> print("Temporal edges:", TG.temporal_size())

   Temporal nodes: 6
   Temporal edges: 8

.. note::

   The temporal order and size of a temporal graph match the length of
   :func:`~networkx_temporal.TemporalGraph.temporal_nodes` and
   :func:`~networkx_temporal.TemporalGraph.temporal_edges`, i.e.,
   the sets of all (**unique**) nodes and edges across all snapshots.


Total order and size
^^^^^^^^^^^^^^^^^^^^

Obtaining the sum of the numbers of nodes and edges (interactions) across all snapshots, with duplicates:

.. code-block:: python

   >>> print("Total nodes:", TG.total_order())  # TG.total_order() != TG.temporal_order()
   >>> print("Total edges:", TG.total_size())   # TG.total_size()  == TG.temporal_size()

   Total nodes: 12
   Total edges: 8

.. note::

   The temporal order and size of a temporal graph match the sum of
   :func:`nodes` and :func:`edges`, i.e.,
   the lists of all (**non-unique**) nodes and edges across all snapshots.


Temporal node neighborhoods
---------------------------

The :func:`~networkx_temporal.TemporalGraph.temporal_neighbors` method returns a dictionary containing node neighbors in all snapshots:

.. code-block:: python

   >>> TG.temporal_neighbors("c")

   {'b'}

Converting the graph to undirected, we also obtain nodes that have node :math:`c` as their neighbor:

.. code-block:: python

   >>> TG.to_undirected().temporal_neighbors("c")

   {'a', 'b', 'd'}
