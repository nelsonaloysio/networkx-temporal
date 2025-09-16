.. include:: ../include-examples.rst


######################
Algorithms and metrics
######################

Algorithms implemented by NetworkX can be called on graph snapshots, while
`NetworkX graph <https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph>`__
methods are inherited by
:class:`~networkx_temporal.classes.TemporalGraph` objects.
This section highlights a few common examples.

.. note::

   Contributions are welcome! If you would like to see a specific algorithm for temporal graphs
   implemented, please feel free to submit a pull request on the package's `GitHub repository
   <https://github.com/nelsonaloysio/networkx-temporal>`__.


Order and size
==============

The methods
:func:`~networkx_temporal.classes.TemporalGraph.order`
and :func:`~networkx_temporal.classes.TemporalGraph.size`
return the number of nodes and edges in each graph snapshot, respectively,
while an additional argument ``copies`` allows specifying whether to count
duplicates:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.TemporalMultiDiGraph()
   >>> # TG = tx.temporal_graph(directed=True, multigraph=True)
   >>>
   >>> TG.add_edge("a", "b", time=0)
   >>> TG.add_edge("c", "b", time=1)
   >>> TG.add_edge("c", "b", time=1)   # <- parallel edge
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

Note that when printing a :class:`~networkx_temporal.classes.TemporalGraph` instance, the order of
the graph :math:`|\mathcal{V}|` corresponds to the number of unique nodes and its size to the
number of edge interactions :math:`|\mathcal{E}|` (with parallel edges):

.. code-block:: python

   >>> print("Order:", TG.order())
   >>> print("Order (unique nodes):", TG.order(copies=False))
   >>> print("Order (including copies):", TG.order(copies=True))

   Order: [3, 2, 4, 4]
   Order (unique nodes): 6
   Order (including copies): 13

.. code-block:: python

   >>> print("Size:", TG.size())
   >>> print("Size (unique edges):", TG.size(copies=False))
   >>> print("Size (including copies):", TG.size(copies=True))

   Size: [2, 1, 3, 3]
   Size (unique edges): 8
   Size (including copies): 9

Visualizing the graph with :func:`~networkx_temporal.draw`, however, shows all nodes
and edges, including their copies:

.. code-block:: python

   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8,2))

.. image:: ../../assets/figure/fig-0.png
   :align: center


.. seealso::

   The alias methods:
   :func:`~networkx_temporal.classes.TemporalGraph.temporal_order`,
   :func:`~networkx_temporal.classes.TemporalGraph.temporal_size`,
   :func:`~networkx_temporal.classes.TemporalGraph.total_order`,
   and :func:`~networkx_temporal.classes.TemporalGraph.total_size`.


Graph centralization
====================

Centralization [1]_ is a graph-level metric that compares the sum of all node centralities against the
maximum possible score for a graph with the same properties, e.g., order, size, and directedness.


Degree centralization
---------------------

The :func:`~networkx_temporal.algorithms.degree_centralization` function returns the score
considering node degrees per snapshot:

.. code-block:: python

   >>> tx.degree_centralization(TG)
   >>> # tx.in_degree_centralization(TG)
   >>> # tx.out_degree_centralization(TG)

   [0, 0, 0.3333333333333333, 1.0]

.. note::

   In directed graphs, the in-degree and out-degree centralization scores may differ:

   .. code-block:: python

      >>> tx.in_degree_centralization(TG) == tx.out_degree_centralization(TG)

      False

   .. code-block:: python

      >>> for t, G in enumerate(TG):
      >>>     indc = tx.in_degree_centralization(G)
      >>>     outdc = tx.out_degree_centralization(G)
      >>>     print(f"t={t}: in={indc:.2f}, out={outdc:.2f}")

      t=0: in=1.00, out=0.25
      t=1: in=1.00, out=1.00
      t=2: in=0.56, out=0.56
      t=3: in=0.11, out=1.00

For example, the theoretical graph corresponding to the maximum degree centralization is a
`star-like structure <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.star_graph.html>`__,
where one central node is connected to all other nodes in the graph, which are not connected among
themselves. Such a graph corresponds to a degree centralization score of :math:`1.0`:

.. code-block:: python

   >>> G = nx.star_graph(10)
   >>> tx.draw(G, layout="fruchterman_reingold")

.. image:: ../../assets/figure/fig-star.png
   :align: center


Note that while edge directedness is considered, self-loops and isolates are ignored by default.
This behavior may be changed by passing ``isolates=True`` or ``self_loops=True`` arguments,
respectively:

.. code-block:: python

   >>> G.add_node(-1)    # Disconnected node.
   >>> G.add_edge(0, 0)  # Edge self-loop.
   >>>
   >>> print(f"Default: {tx.degree_centralization(G)}\n"
   >>>       f"With isolates: {tx.degree_centralization(G, isolates=True):.3f}\n"
   >>>       f"With self-loops: {tx.degree_centralization(G, self_loops=True):.3f}\n"
   >>>       f"With both: {tx.degree_centralization(G, isolates=True, self_loops=True):.3f}")

   Default: 1.0
   With isolates: 0.909
   With self-loops: 1.222
   With both: 1.109


More centralization metrics
---------------------------

The :func:`~networkx_temporal.algorithms.centralization` function receives the node centrality
values for a static or temporal graph, plus an optional ``scalar`` value corresponding to the
maximum possible sum of node centrality differences in a theoretical likewise graph, and returns
the centralization score for the graph.

.. code-block:: python

   >>> centrality = G.degree()
   >>> scalar = sum(G.order() - 2 for n in range(G.order()-1))  # |V|-1 for DiGraph
   >>>
   >>> centralization = tx.centralization(centrality=centrality, scalar=scalar)
   >>> print(f"Degree centralization: {centralization:.2f}")

   1.00

The function may be used to calculate the score for other centrality measures,
e.g., closeness and betweenness, where the most centralized structure is a star-like graph,
or eigenvector centrality, where the most centralized structure is a graph with a single edge
(and potentially many isolates).

.. seealso::

   The `igraph documentation on the centralization of a graph <https://igraph.org/r/html/1.3.5/centralize.html>`__
   for additional implementations.


Node centrality
===============

The functions and algorithms implemented by NetworkX can be applied directly on the temporal graph
by iterating over snapshots. For instance, to calculate the `Katz centrality
<https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.katz_centrality.html>`__
for each snapshot:

.. code-block:: python

   >>> TG = tx.from_multigraph(TG)
   >>>
   >>> for t, G in enumerate(TG):
   >>>     katz = nx.katz_centrality(G)
   >>>     katz = {node: round(value, 2) for node, value in katz.items()}
   >>>     print(f"t={t}: {katz}")

   t=0: {'a': 0.54, 'b': 0.65, 'c': 0.54}
   t=1: {'c': 0.67, 'b': 0.74}
   t=2: {'a': 0.46, 'c': 0.56, 'd': 0.46, 'e': 0.51}
   t=3: {'f': 0.46, 'e': 0.51, 'a': 0.51, 'b': 0.51}

Note that we first converted the multigraph to a simple graph (without parallel edges) using the
:func:`~networkx_temporal.utils.from_multigraph` function, as the algorithm implementation
does not support multigraphs.

.. seealso::

   The `Algorithms section <https://networkx.org/documentation/stable/reference/algorithms/index.html>`__
   of the NetworkX documentation for a list of available functions.


Node degree
-----------

In addition, any `NetworkX graph methods
<https://networkx.org/documentation/stable/reference/classes/graph.html#methods>`__
can be called directly from the temporal graph.
For example, the methods
:func:`~networkx_temporal.algorithms.degree`
:func:`~networkx_temporal.algorithms.in_degree`
and
:func:`~networkx_temporal.algorithms.out_degree`
return the results per snapshot:

.. code-block:: python

   >>> TG.degree()
   >>> # TG.in_degree()
   >>> # TG.out_degree()

   [{'a': 1, 'b': 2, 'c': 1},
    {'c': 1, 'b': 1},
    {'a': 1, 'c': 2, 'd': 2, 'e': 1},
    {'f': 3, 'e': 1, 'a': 1, 'b': 1}]

.. code-block:: python

   >>> TG.degree("a")
   >>> # TG.in_degree("a")
   >>> # TG.out_degree("a")

   [1, None, 1, 1]


Note that, for :math:`a` in :math:`t=1` above, a ``None`` is returned as the node is not
present in that snapshot.

Degree centrality
-----------------

Alternatively, :func:`~networkx_temporal.algorithms.degree_centrality`
returns the fraction of nodes connected to each of all nodes:

.. code-block:: python

   >>> tx.degree_centrality(TG)
   >>> # tx.in_degree_centrality(TG)
   >>> # tx.out_degree_centrality(TG)

   {'a': 0.6, 'b': 0.8, 'c': 0.8, 'd': 0.4, 'e': 0.4, 'f': 0.6}

.. code-block:: python

   >>> tx.degree_centrality(TG, "a")
   >>> # tx.in_degree_centrality(TG, "a")
   >>> # tx.out_degree_centrality(TG, "a")

   0.6

Note that the degree centrality is calculated considering the unique nodes on the whole graph.


Total degree
^^^^^^^^^^^^

Likewise, the :func:`~networkx_temporal.algorithms.degree` function
returns a dictionary with the sum of node degrees over time:

.. code-block:: python

   >>> tx.degree(TG)
   >>> # tx.in_degree(TG)
   >>> # tx.out_degree(TG)

   {'a': 3, 'b': 4, 'c': 4, 'd': 2, 'e': 2, 'f': 3}

.. code-block:: python

   >>> tx.degree(TG, "a")
   >>> # tx.in_degree(TG, "a")
   >>> # tx.out_degree(TG, "a")

   3

.. seealso::

   The alias methods
   :func:`~networkx_temporal.classes.TemporalGraph.total_degree`,
   :func:`~networkx_temporal.classes.TemporalGraph.total_in_degree`,
   and :func:`~networkx_temporal.classes.TemporalGraph.total_out_degree`,
   which return a dictionary with the sum of node degrees over time,
   while maintaining its original ordering.


Neighbors
=========

Edge directedness is considered when obtaining the neighbors of a node,
either per snapshot or considering all snapshots, via
the :func:`~networkx_temporal.classes.TemporalGraph.neighbors` method
and the :func:`~networkx_temporal.classes.neighbors` function, respectively.


Per snapshot
------------

The :func:`~networkx_temporal.classes.TemporalGraph.neighbors`
method returns a generator over graph snapshots, respecting edge direction:

.. code-block:: python

   >>> TG = TG.slice(attr="time")
   >>> list(TG.neighbors("c"))

   [[], ['b'], [], []]

Converting the graph to undirected, we also obtain nodes that have node
:math:`c` as their neighbor:

.. code-block:: python

   >>> list(TG.to_undirected().neighbors("c"))

   [[], ['b'], ['a', 'd'], []]

.. hint::

   The above is effectively the same as calling the
   :func:`~networkx_temporal.classes.TemporalGraph.all_neighbors`
   method instead.


From all snapshots
------------------

The :func:`~networkx_temporal.classes.neighbors` function
returns node neighborhoods considering all snapshots:

.. code-block:: python

   >>> list(tx.neighbors(TG, "c"))

   ['b']

Converting the graph to undirected, we also obtain temporal nodes that have it
as their neighbor:

.. code-block:: python

   >>> list(tx.neighbors(TG.to_undirected(), "c"))

   ['a', 'd', 'b']

Indexes allow to restrict the search to specific snapshots in time, e.g.,
from :math:`t=0` to :math:`t=1`:

.. code-block:: python

   >>> list(tx.neighbors(TG[0:2], "c"))

   ['b']

.. note::

   Indexing follows Python conventions and is inclusive on the left and exclusive on the right,
   i.e., the above example returns the neighbors of node :math:`c` at time steps :math:`t=0` and
   :math:`t=1`.

-----

.. [1] Freeman, L.C. (1979).
       Centrality in Social Networks I: Conceptual Clarification.
       Social Networks 1, 215--239.
       doi: `10.1016/0378-8733(78)90021-7 <https://doi.org/10.1016/0378-8733(78)90021-7>`__