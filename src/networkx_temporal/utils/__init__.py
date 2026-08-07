"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary - Temporal Graph utilities

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
)