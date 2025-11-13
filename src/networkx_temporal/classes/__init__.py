"""
Classes and functions for temporal graph objects.

.. rubric:: Classes - Summary

.. autosummary::

   TemporalGraph
   TemporalDiGraph
   TemporalMultiGraph
   TemporalMultiDiGraph
   TemporalABC

.. rubric:: Factory Functions - Summary

.. autosummary::

   temporal_graph
   empty_graph

.. rubric:: Functions - Summary

.. autosummary::

   all_neighbors
   compose
   compose_all
   from_multigraph
   is_frozen
   is_static_graph
   is_temporal_graph
   is_unrolled_graph
   neighbors
   relabel_nodes
   to_multigraph

.. rubric:: Classes

.. autoclass:: networkx_temporal.classes.TemporalGraph
   :members:
   :inherited-members: Graph

.. autoclass:: networkx_temporal.classes.TemporalDiGraph
   :members:

.. autoclass:: networkx_temporal.classes.TemporalMultiGraph
   :members:

.. autoclass:: networkx_temporal.classes.TemporalMultiDiGraph
   :members:

.. autoclass:: TemporalABC

.. rubric:: Functions
"""

from .abc import TemporalABC
from .digraph import TemporalDiGraph
from .factory import temporal_graph, empty_graph
from .functions import (
    all_neighbors,
    compose,
    compose_all,
    create_empty_copy,
    from_multigraph,
    neighbors,
    relabel_nodes,
    to_multigraph,
    set_edge_attributes,
    set_node_attributes,
)
from .graph import TemporalGraph
from .multidigraph import TemporalMultiDiGraph
from .multigraph import TemporalMultiGraph
from .types import (
    is_frozen,
    is_static_graph,
    is_temporal_graph,
    is_unrolled_graph,
)

__all__ = (
    "TemporalGraph",
    "TemporalDiGraph",
    "TemporalMultiGraph",
    "TemporalMultiDiGraph",
    "TemporalABC",
    "all_neighbors",
    "compose",
    "compose_all",
    "create_empty_copy",
    "empty_graph",
    "from_multigraph",
    "is_frozen",
    "is_static_graph",
    "is_temporal_graph",
    "is_unrolled_graph",
    "neighbors",
    "relabel_nodes",
    "set_edge_attributes",
    "set_node_attributes",
    "temporal_graph",
    "to_multigraph",
)