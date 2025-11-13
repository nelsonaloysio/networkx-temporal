"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary

.. autosummary::

   combine_snapshots
   edge_to_node_attr
   get_edge_attributes
   get_node_attributes
   node_to_edge_attr
   partitions
   propagate_snapshots

.. rubric:: Converters - Summary

.. autosummary::

   convert.convert
   convert.to_dgl
   convert.to_dynetx
   convert.to_graph_tool
   convert.to_igraph
   convert.to_networkit
   convert.to_snap
   convert.to_stellargraph
   convert.to_teneto
   convert.to_torch_geometric

.. rubric:: Functions
"""

from .utils import (
    combine_snapshots,
    edge_to_node_attr,
    get_edge_attributes,
    get_node_attributes,
    node_to_edge_attr,
    partitions,
    propagate_snapshots,
)

__all__ = (
    "combine_snapshots",
    "edge_to_node_attr",
    "get_edge_attributes",
    "get_node_attributes",
    "node_to_edge_attr",
    "partitions",
    "propagate_snapshots",
)