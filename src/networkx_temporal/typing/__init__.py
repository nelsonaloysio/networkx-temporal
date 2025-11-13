"""
Type hints exclusively used in function definitions.

.. rubric:: Summary

.. autosummary::

   Literal
   Figure
   StaticGraph
   TemporalGraph
   TemporalDiGraph
   TemporalMultiGraph
   TemporalMultiDiGraph

.. rubric:: Note

Type hints are used to specify the type of arguments and return values in function definitions
only, and may not be used to check an object type at runtime, as demonstrated in the example below.

.. code-block:: python

    >>> from networkx_temporal import TemporalGraph
    >>> from networkx_temporal.typing import TemporalGraph as TemporalGraphType
    >>>
    >>> TG = TemporalGraph()
    >>> isinstance(TG, TemporalGraph), isinstance(TG, TemporalGraphType)

    (True, False)

.. note::

   The convenience functions :func:`~networkx_temporal.classes.is_temporal_graph`
   and :func:`~networkx_temporal.classes.is_static_graph`
   may be used instead to check if an object is an instance of a temporal or
   static NetworkX graph.
"""

from .typing import (
    Literal,
    Figure,
    StaticGraph,
    TemporalGraph,
    TemporalDiGraph,
    TemporalMultiGraph,
    TemporalMultiDiGraph,
)
