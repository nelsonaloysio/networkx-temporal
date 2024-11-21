"""
Classes and functions for handling temporal graphs.

.. rubric:: Summary

.. autosummary::

   TemporalGraph
   TemporalDiGraph
   TemporalMultiGraph
   TemporalMultiDiGraph
   TemporalBase
   is_frozen
   is_temporal_graph
   temporal_graph

.. rubric:: Classes

.. autoclass:: networkx_temporal.graph.TemporalGraph
   :members:
   :inherited-members: Graph

.. autoclass:: networkx_temporal.graph.TemporalDiGraph
   :members:

.. autoclass:: networkx_temporal.graph.TemporalMultiGraph
   :members:

.. autoclass:: networkx_temporal.graph.TemporalMultiDiGraph
   :members:

.. autoclass:: TemporalBase

.. rubric:: Functions
"""

from .base import TemporalBase, is_frozen, is_temporal_graph
from .digraph import TemporalDiGraph
from .factory import temporal_graph
from .graph import TemporalGraph
from .multidigraph import TemporalMultiDiGraph
from .multigraph import TemporalMultiGraph

__all__ = (
    "TemporalGraph",
    "TemporalDiGraph",
    "TemporalMultiGraph",
    "TemporalMultiDiGraph",
    "TemporalBase",
    "is_frozen",
    "is_temporal_graph",
    "temporal_graph",
)