.. note::

   This documentation was generated on |today| for package release |release|.

.. toctree::
   :hidden:
   :caption: Introduction

   Overview <self>

.. toctree::
   :hidden:
   :caption: Package reference
   :glob:

   api/api
   api/algorithms
   api/classes
   api/drawing
   api/generators
   api/readwrite
   api/transform
   api/typing
   api/utils

.. toctree::
   :hidden:
   :caption: Examples

   examples/basics
   examples/convert
   examples/metrics
   examples/community

.. toctree::
   :hidden:
   :caption: Appendix

   cite
   references
   genindex

#################
NetworkX-Temporal
#################

.. image:: https://badge.fury.readwrite/py/networkx-temporal.svg
   :target: https://pypi.org/project/networkx-temporal/
   :alt: PyPI version

.. image:: https://readthedocs.org/projects/networkx-temporal/badge/?version=latest
   :target: https://networkx-temporal.readthedocs.readwrite/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://static.pepy.tech/badge/networkx-temporal
   :target: https://pepy.tech/project/networkx-temporal?versions=*
   :alt: Downloads

.. image:: https://static.pepy.tech/badge/networkx-temporal/month
   :target: https://pepy.tech/project/networkx-temporal?versions=*
   :alt: Downloads

.. image:: https://img.shields.readwrite/pypi/l/networkx-temporal
   :target: https://github.com/nelsonaloysio/networkx-temporal/blob/main/LICENSE.md
   :alt: License


**NetworkX-Temporal** extends the `NetworkX <https://networkx.org>`__ library to dynamic graphs,
i.e., temporal network data.

This package provides new :class:`~networkx_temporal.classes.TemporalGraph` classes, which inherit
NetworkX's `graph classes <https://networkx.org/documentation/stable/reference/classes/index.html>`_
and implement additional functions to manipulate temporal data within. Among others, it provides
ways to :func:`~networkx_temporal.classes.TemporalGraph.slice` a graph into snapshots and
:mod:`~networkx_temporal.transform` or :mod:`~networkx_temporal.utils.convert` it
to other libraries and formats.


Install
=======

The package supports **Python 3.7+** and is readily available from `PyPI
<https://pypi.org/project/networkx-temporal/>`__:

.. code-block:: bash

   $ pip install networkx-temporal

Additional support for plotting graphs may be optionally installed with:

.. code-block:: bash

   $ pip install 'networkx-temporal[draw]'


Quick start
===========

The following is a quick example of the package in action, covering its basic functionality.
More examples are accessible via the sidebar and also available as a
`Jupyter notebook
<https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__
(`open on Colab
<https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal.ipynb>`__).


Build and slice temporal graph
------------------------------

Create a directed :class:`~networkx_temporal.classes.TemporalGraph` object and
:func:`~networkx_temporal.classes.TemporalGraph.slice` it into a number of snapshots:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>>
   >>> TG = tx.temporal_graph() # TG = tx.TemporalMultiGraph()
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
   >>> print(TG)

   TemporalMultiGraph (t=4) with 6 nodes and 8 edges

The ``attr`` parameter optionally defines the attribute name to use for slicing the temporal graph,
while the number of snapshots to be created may likewise be specified with the ``bins`` parameter:

.. code-block:: python

   >>> TG.slice(attr="time", bins=2)

   TemporalMultiGraph (t=2) with 6 nodes and 8 edges

Note that the total number of nodes may vary, while the total number of edges is preserved.

.. note::

   The :func:`~networkx_temporal.classes.TemporalGraph.slice` method by default creates a snapshot
   for unique time value in the temporal graph. It internally stores `views
   <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
   of the original graph, so no data is copied unless otherwise specified.


Plot snapshots
--------------

We may visualize the resulting temporal graph using the :func:`~networkx_temporal.drawing.draw` function:

.. code-block:: python

   >>> tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))

.. image:: (https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/assets/figure/temporal-graph.png)
   :alt: Temporal graph plot
   :align: center


Save and load data
------------------

The :func:`~networkx_temporal.readwrite.write_graph` and :func:`~networkx_temporal.readwrite.read_graph`
functions accept compressed temporal graphs:

.. code-block:: python

   >>> TG = tx.read_graph("temporal-graph.graphml.zip")
   >>> tx.write_graph(TG, "temporal-graph.graphml.zip")

Both functions support the same `extension formats
<https://networkx.org/documentation/stable/reference/io/index.html>`__
as in the installed NetworkX library version.


Convert and transform graphs
----------------------------

This package allows to transform a :class:`~networkx_temporal.classes.TemporalGraph` between different
`graph representations <examples/convert.html#graph-representations>`__:

* `Static graphs <examples/convert.html#static-graph>`__:
  flattened or aggregated version of the temporal graph.
* `Snapshot-based temporal graphs <examples/convert.html#snapshot-based-temporal-graph>`__:
  a list of node- or edge-level snapshots.
* `Event-based temporal graphs <examples/convert.html#event-based-temporal-graph>`__:
  a sequence of edge-level events (interactions).
* `Unrolled temporal graphs <examples/convert.html#unrolled-temporal-graph>`__:
  a single graph with time-stamped nodes and edges.

.. code-block:: python

   >>> G = TG.to_static()        # TG = tx.from_static(G)
   >>> STG = TG.to_snapshots()   # TG = tx.from_snapshots(SG)
   >>> ETG = TG.to_events()      # TG = tx.from_events(EG)
   >>> UTG = TG.to_unrolled()    # TG = tx.from_unrolled(UG)

In addition, both static and temporal graphs may be converted to the following
`graph formats <examples/convert.html#graph-formats>`__:

- `Deep Graph Library <https://www.dgl.ai>`__
- `DyNetX <https://dynetx.readthedocs.readwrite>`__
- `graph-tool <https://graph-tool.skewed.de>`__
- `igraph <https://igraph.org/python/>`__
- `NetworKit <https://networkit.github.readwrite>`__
- `NumPy <https://numpy.org/>`__
- `PyTorch Geometric <https://pytorch-geometric.readthedocs.readwrite>`__
- `Stanford Network Analysis Platform <https://snap.stanford.edu>`__
- `SciPy <https://scipy.org>`__
- `StellarGraph <https://stellargraph.readthedocs.readwrite>`__
- `Teneto <https://teneto.readthedocs.readwrite>`__

.. code-block:: python

   >>> tx.convert(G, "igraph")

   <igraph.Graph at 0x7f048ef52c50>


Links
=====

For more information on using this package, please refer to the following sections:

- `Package reference <api/api.html>`__ for details on the classes and functions implemented by each module.

- `Examples <examples/basics.html>`__ covering some of its main functionalities and most common use cases.

.. seealso::

   The package's `GitHub repository <https://github.com/nelsonaloysio/networkx-temporal>`__
   for the latest updates and issues. Contributions are welcome!

If you have any questions or feedback to share, please also feel free to
`contact us via e-mail <mailto:nelson.reis@phd.unipi.it>`__. |:mailbox_with_mail:|
