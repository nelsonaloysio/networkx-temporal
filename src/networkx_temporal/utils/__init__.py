"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary

.. autosummary::

   combine_snapshots
   get_edge_attributes
   get_node_attributes
   get_unique_edge_attributes
   get_unique_node_attributes
   map_attr_to_edges
   map_attr_to_nodes
   map_edge_attr_to_nodes
   map_node_attr_to_edges
   map_partitions_to_edges
   map_partitions_to_nodes
   partition_edges
   partition_nodes
   propagate_snapshots
   temporal_edge_matrix
   temporal_node_matrix

.. rubric:: Converters - Summary

.. autosummary::

   convert.convert
   convert.to_dgl
   convert.to_dynetx
   convert.to_graph_tool
   convert.to_igraph
   convert.to_networkit
   convert.to_numpy
   convert.to_scipy
   convert.to_snap
   convert.to_stellargraph
   convert.to_teneto
   convert.to_torch_geometric

.. rubric:: Functions
"""

from .utils import *

__all__ = (
    "combine_snapshots",
    "get_edge_attributes",
    "get_node_attributes",
    "get_unique_edge_attributes",
    "get_unique_node_attributes",
    "map_attr_to_edges",
    "map_attr_to_nodes",
    "map_edge_attr_to_nodes",
    "map_node_attr_to_edges",
    "map_partitions_to_edges",
    "map_partitions_to_nodes",
    "partition_edges",
    "partition_nodes",
    "propagate_snapshots",
    "temporal_edge_matrix",
    "temporal_node_matrix",
)