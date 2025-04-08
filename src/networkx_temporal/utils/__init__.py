"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary

.. autosummary::

   from_multigraph
   is_frozen
   is_static_graph
   is_temporal_graph
   partitions
   to_multigraph

.. rubric:: Summary - Converters

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
    from_multigraph,
    is_frozen,
    is_static_graph,
    is_temporal_graph,
    partitions,
    to_multigraph,
)

__all__ = (
    "from_multigraph",
    "is_frozen",
    "is_static_graph",
    "is_temporal_graph",
    "partitions",
    "to_multigraph",
)