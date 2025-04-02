"""
Classes and functions for handling temporal graphs.

.. rubric:: Summary

.. autosummary::

   TemporalGraph
   TemporalDiGraph
   TemporalMultiGraph
   TemporalMultiDiGraph
   TemporalABC
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

.. autoclass:: TemporalABC

.. rubric:: Functions
"""

from .abc import TemporalABC
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
    "TemporalABC",
    "temporal_graph",
)