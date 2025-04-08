"""
Classes and functions for handling temporal graphs.

.. rubric:: Summary - Classes

.. autosummary::

   TemporalGraph
   TemporalDiGraph
   TemporalMultiGraph
   TemporalMultiDiGraph
   TemporalABC

.. rubric:: Summary - Functions

.. autosummary::

   all_neighbors
   neighbors
   temporal_graph

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
from .factory import temporal_graph
from .functions import (
    all_neighbors,
    neighbors,
)
from .graph import TemporalGraph
from .multidigraph import TemporalMultiDiGraph
from .multigraph import TemporalMultiGraph

__all__ = (
    "TemporalGraph",
    "TemporalDiGraph",
    "TemporalMultiGraph",
    "TemporalMultiDiGraph",
    "TemporalABC",
    "all_neighbors",
    "neighbors",
    "temporal_graph",
)