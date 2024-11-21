.. include:: ../include-examples.rst

######################
Metrics and algorithms
######################

Both static and temporal graph metrics can be calculated from a
:class:`~networkx_temporal.graph.TemporalGraph` object. This section showcases a few common examples
using some of NetworkX's built-in functions and algorithms.

.. note::

   Contributions are welcome! If you would like to see a specific algorithm for temporal graphs
   implemented, please feel free to submit a pull request on the package's `GitHub repository
   <https://github.com/nelsonaloysio/networkx-temporal>`__.


Static graph metrics
====================

The functions and algorithms implemented by NetworkX can be applied directly on the temporal graph
by iterating over snapshots. For instance, to calculate the `Katz centrality
<https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.katz_centrality.html>`__
for each snapshot:

.. code-block:: python

   >>> import networkx as nx
   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalDiGraph()  # TG = tx.temporal_graph(directed=True, multigraph=False)
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
   >>> for t, G in enumerate(TG):
   >>>     katz = nx.katz_centrality(G)
   >>>     katz = {node: round(value, 3) for node, value in katz.items()}
   >>>     print(f"t={t}: {katz}")

   # t=0: {'a': 0.673, 'b': 0.74}
   # t=1: {'c': 0.673, 'b': 0.74}
   # t=2: {'a': 0.464, 'c': 0.556, 'd': 0.464, 'e': 0.51}
   # t=3: {'a': 0.511, 'b': 0.511, 'e': 0.511, 'f': 0.465}

In addition, any NetworkX `Graph methods
<https://networkx.org/documentation/stable/reference/classes/graph.html#methods>`__
can be called directly from the temporal graph as well. Doing so will automatically apply it to each
snapshot separately, as seen in the examples below.

.. seealso::

   The `Algorithms section <https://networkx.org/documentation/stable/reference/algorithms/index.html>`__
   of the NetworkX documentation for a list of available functions.


Degree centrality
-----------------

Static graph methods such as
`degree <https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.degree.html>`__,
`in_degree <https://networkx.org/documentation/stable/reference/classes/generated/networkx.DiGraph.in_degree.html>`__, and
`out_degree <https://networkx.org/documentation/stable/reference/classes/generated/networkx.DiGraph.out_degree.html>`__
return the results per snapshot:

.. code-block:: python

   >>> TG.degree()

   [DiDegreeView({'b': 1, 'a': 1}),
    DiDegreeView({'c': 1, 'b': 1}),
    DiDegreeView({'a': 1, 'c': 2, 'd': 2, 'e': 1}),
    DiDegreeView({'a': 1, 'b': 1, 'e': 1, 'f': 3})]

Alternatively, we may also obtain the degree of a specific node in a given snapshot, e.g., node :math:`a_0`:

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

The `neighbors <https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.neighbors.html>`__
method returns a list of neighbors for each node in each snapshot:

.. code-block:: python

   >>> TG.neighbors("c")

   [[], ['b'], [], []]

Converting the graph to undirected, we also obtain nodes that have node :math:`c` as their neighbor:

.. code-block:: python

   >>> TG.to_undirected().neighbors("c")

   [[], ['b'], ['a', 'd'], []]


-----


Temporal graph metrics
======================

Only a few methods that consider all snapshots are currently available from :class:`~networkx_temporal.graph.TemporalGraph` objects.
They mostly serve as wrappers of methods implemented by NetworkX, for convenience purposes.


Temporal degree centrality
--------------------------

The :func:`~networkx_temporal.graph.TemporalGraph.temporal_degree` method returns a dictionary containing node degrees across all time steps:

.. code-block:: python

   >>> TG.temporal_degree()

   {'a': 3, 'f': 3, 'e': 2, 'd': 2, 'c': 3, 'b': 3}

Alternatively, to obtain the degree of a specific node considering all snapshots, e.g., node :math:`a`:

.. code-block:: python

   >>> TG.temporal_degree("a")

   3


Temporal order and size
-----------------------

The :func:`~networkx_temporal.graph.TemporalGraph.temporal_order` and
:func:`~networkx_temporal.graph.TemporalGraph.temporal_size` functions return the total unique nodes and edges:

.. code-block:: python

   >>> print("Temporal nodes:", TG.temporal_order())
   >>> print("Temporal edges:", TG.temporal_size())

   Temporal nodes: 6
   Temporal edges: 8

.. note::

   The temporal order and size of a temporal graph match the length of
   :func:`~networkx_temporal.graph.TemporalGraph.temporal_nodes` and
   :func:`~networkx_temporal.graph.TemporalGraph.temporal_edges`, i.e.,
   the sets of all (**unique**) nodes and edges considering all snapshots.


Alternatively,
:func:`~networkx_temporal.graph.TemporalGraph.total_order` and
:func:`~networkx_temporal.graph.TemporalGraph.total_size` return the sum of nodes and edges per snapshot:

.. code-block:: python

   >>> print("Total nodes:", TG.total_order())  # TG.total_order() != TG.temporal_order()
   >>> print("Total edges:", TG.total_size())   # TG.total_size()  == TG.temporal_size()

   Total nodes: 12
   Total edges: 8

.. note::

   The total order and size of a temporal graph match the sum of lenghts of
   :func:`nodes` and :func:`edges`, i.e.,
   the lists of all (**non-unique**) nodes and edges considering each snapshot separately.


Temporal node neighborhoods
---------------------------

The :func:`~networkx_temporal.graph.TemporalGraph.temporal_neighbors` method returns a dictionary containing node neighbors in all snapshots:

.. code-block:: python

   >>> TG.temporal_neighbors("c")

   {'b'}

Converting the graph to undirected, we also obtain nodes that have node :math:`c` in their neighborhood:

.. code-block:: python

   >>> TG.to_undirected().temporal_neighbors("c")

   {'a', 'b', 'd'}

Lastly, we may also restrict the search to a specific snapshot or time window, e.g., from :math:`t=2` to :math:`t=4`:

.. code-block:: python

   >>> TG.temporal_neighbors("c", start=2, end=4)

   {'a', 'd'}

.. note::

   The method :func:`~networkx_temporal.graph.TemporalGraph.temporal_neighbors` returns a set of neighbors
   considering all snapshots, while the method :func:`~networkx_temporal.graph.TemporalGraph.neighbors`
   returns a list of neighbors for each node in each snapshot.