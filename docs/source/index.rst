.. toctree::
   :hidden:
   :caption: Introduction

   Overview <self>

.. toctree::
   :hidden:
   :caption: Main documentation

   guide
   api
   cite

.. toctree::
   :hidden:
   :caption: Appendix

   references
   genindex

.. important::

   This documentation was generated on |today| for package release |release|.

#################
networkx-temporal
#################

**networkx-temporal** extends the `NetworkX <https://networkx.org>`__ library to dynamic networks,
i.e., temporal graph data.

This package provides a new class, `TemporalGraph <documentation.html#networkx_temporal.TemporalGraph>`_,
which extends ``networkx`` main
`Graph <https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph>`_
class and implements additional functions to manipulate
temporal data within. Most importantly, it provides methods to `slice <documentation.html#networkx_temporal.slice>`__
graphs into snapshots and convert between different formats and representations.

.. note::

   At the moment, this package does not provide new methods to analyze temporal graphs, such as computing
   temporal centrality measures, or detecting temporal communities --- although it makes it arguably
   easier to implement such methods on top of it (see some of the `Examples <examples.html>`_).

Install
=======

The package is readily available from `PyPI <https://pypi.org/project/networkx-temporal/>`_:

.. code-block:: bash

   pip install networkx-temporal

It supports **Python 3.7+** and has been tested on Linux, Windows, and macOS.


Quick start
===========

The following is a quick example of the package in action, covering its basic functionalities.
For further details on its general usage, please refer to the `Examples <examples.html>`_ and
`Package reference <documentation.html>`_ sections.

Build and slice temporal graph
------------------------------

Quickly create a
`TemporalGraph <documentation.html#networkx_temporal.TemporalGraph>`_
object and
`slice <documentation.html#networkx_temporal.TemporalGraph.slice>`_
it into a number of snapshots:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>> from networkx_temporal.example.draw import draw_temporal_graph
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
   >>> TG = TG.slice(attr="time")
   >>>
   >>> print(TG)

.. code-block:: none

   TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges

The ``slice`` method by default creates a snapshot for each unique time value in the temporal graph.
It internally stores views of the original graph data, so no data is copied unless specified otherwise.

Plot temporal graph
^^^^^^^^^^^^^^^^^^^

We may visualize the resulting temporal graph using the `draw_temporal_graph <documentation.html#networkx_temporal.draw.draw_temporal_graph>`_ function:

.. code-block:: python

   from networkx_temporal.example.draw import draw_temporal_graph

   draw_temporal_graph(TG, figsize=(8, 2))

.. image:: ../figure/fig_7.png

.. note::

   The ``draw_temporal_graph`` function currently simply calls ``networkx``
   `draw <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`_
   in the back-end and is meant only as an example to showcase the package's capabilities. It does
   not scale well to large graphs, which usually require more sophisticated approaches or specialized
   visualization tools.

Convert and transform graph
---------------------------

This package provides a set of functions to convert to different graph formats and representations:

- `convert <documentation.html#networkx_temporal.convert>`_: Convert static graph object among different packages.
- `from_events <documentation.html#networkx_temporal.from_events>`_: Create a ``TemporalGraph`` from a list of events.
- `from_snapshots <documentation.html#networkx_temporal.from_snapshots>`_: Create a ``TemporalGraph`` from a list of snapshots.
- `from_static <documentation.html#networkx_temporal.from_static>`_: Create a ``TemporalGraph`` from a static graph.
- `from_unified <documentation.html#networkx_temporal.from_unified>`_: Create a ``TemporalGraph`` from a unified graph.
- `to_events <documentation.html#networkx_temporal.TemporalGraph.to_events>`_: Transform a ``TemporalGraph`` to a list of events.
- `to_snapshots <documentation.html#networkx_temporal.TemporalGraph.to_snapshots>`_: Transform a ``TemporalGraph`` to a list of snapshots.
- `to_static <documentation.html#networkx_temporal.TemporalGraph.to_static>`_: Transform a ``TemporalGraph`` to a static graph.
- `to_unified <documentation.html#networkx_temporal.TemporalGraph.to_unified>`_: Transform a ``TemporalGraph`` to a unified graph.

As of now, the package supports converting static and temporal graphs to the following formats:

- `Deep Graph Library <https://www.dgl.ai>`_
- `graph-tool <https://graph-tool.skewed.de>`_
- `igraph <https://igraph.org/python/>`_
- `NetworKit <https://networkit.github.io>`_
- `NetworkX <https://networx.org>`_
- `PyTorch Geometric <https://pytorch-geometric.readthedocs.io>`_
- `Teneto <https://teneto.readthedocs.io>`_

Links
=====

For more information on how to use the package, please refer to the following sections:

- `Get started <guide.html>`_ for examples and use cases covering the package's main functionalities.

- `API reference <documentation.html>`_ for further details on its implemented classes and functions.

.. seealso::

   The package's `GitHub repository <https://github.com/nelsonaloysio/networkx-temporal>`_ for the latest updates and issues. Contributions are welcome!

If you have any questions or feedback to share, please also feel free to `contact us via e-mail <mailto:nelson.reis@phd.unipi.it>`_. |:mailbox_with_mail:|