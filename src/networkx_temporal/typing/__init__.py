"""
Type hints exclusively used in function definitions.

.. rubric:: Summary

.. autosummary::

   Literal
   Figure
   StaticGraph
   TemporalGraph

.. rubric:: Note

Type hints are used to specify the type of arguments and return values in function definitions only,
and may not be used to check an object type at runtime, as the following example demonstrates:

.. code-block:: python

    >>> from networkx_temporal import TemporalGraph
    >>> from networkx_temporal.typing import TemporalGraph as TemporalGraphType
    >>>
    >>> TG = TemporalGraph()
    >>> type(TG) == TemporalGraph, type(TG) == TemporalGraphType

    (True, False)

.. note::

   The convenience function :func:`~networkx_temporal.graph.is_temporal_graph` may be used to check
   if an object is an instance of a :class:`~networkx_temporal.graph.TemporalGraph`,
   :class:`~networkx_temporal.graph.TemporalDiGraph`,
   :class:`~networkx_temporal.graph.TemporalMultiGraph`
   or :class:`~networkx_temporal.graph.TemporalMultiDiGraph` class.
"""

from .typing import (
    Literal,
    Figure,
    StaticGraph,
    TemporalGraph,
)
