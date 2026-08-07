"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary - Graph utilities

.. autosummary::

   combine_snapshots
   propagate_snapshots
   temporal_edge_similarity
   temporal_node_similarity
   to_adjacency_matrix
   to_supra_adjacency_matrix

.. rubric:: Summary - Node utilities

.. autosummary::

   get_node_attributes
   get_unique_node_attributes
   map_attr_to_nodes
   map_edge_attr_to_nodes
   map_partitions_to_nodes
   partition_nodes

.. rubric:: Summary - Edge utilities

.. autosummary::

   get_edge_attributes
   get_unique_edge_attributes
   map_attr_to_edges
   map_node_attr_to_edges
   map_partitions_to_edges
   partition_edges

.. rubric:: Summary - Conversion utilities

.. autosummary::

   from_numpy
   from_pandas
   from_scipy
   to_cugraph
   to_cupy
   to_dgl
   to_dynetx
   to_graph_tool
   to_igraph
   to_networkit
   to_numpy
   to_pandas
   to_scipy
   to_snap
   to_stellargraph
   to_teneto
   to_torch_geometric

.. rubric:: Note

The :func:`~networkx_temporal.classes.TemporalGraph.convert` wrapper is also available as
a top-level function and as a :class:`~networkx_temporal.classes.TemporalGraph` method:

.. code-block:: python

   >>> import networkx_temporal as tx
   >>> TG = tx.example_sbm_graph()
   >>> TG.convert("igraph")

   [<igraph.Graph at 0x108198950>,
    <igraph.Graph at 0x168589950>,
    <igraph.Graph at 0x168589a50>]

.. code-block:: python

   >>> G = TG.to_static()
   >>> tx.convert(G, "igraph")

   <igraph.Graph at 0x168589150>

.. rubric:: Functions
"""

from .utils import *

__all__ = (
   "combine_snapshots",
   "propagate_snapshots",
   "temporal_edge_similarity",
   "temporal_node_similarity",
   "to_adjacency_matrix",
   "to_supra_adjacency_matrix",
   "get_node_attributes",
   "get_unique_node_attributes",
   "map_attr_to_nodes",
   "map_edge_attr_to_nodes",
   "map_partitions_to_nodes",
   "partition_nodes",
   "get_edge_attributes",
   "get_unique_edge_attributes",
   "map_attr_to_edges",
   "map_node_attr_to_edges",
   "map_partitions_to_edges",
   "partition_edges",
   "convert",
   "from_numpy",
   "from_pandas",
   "from_scipy",
   "to_cugraph",
   "to_cupy",
   "to_dgl",
   "to_dynetx",
   "to_graph_tool",
   "to_igraph",
   "to_networkit",
   "to_numpy",
   "to_pandas",
   "to_scipy",
   "to_snap",
   "to_stellargraph",
   "to_teneto",
   "to_torch_geometric",
)