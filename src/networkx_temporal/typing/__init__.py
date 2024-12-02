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

   The convenience functions :func:`~networkx_temporal.utils.is_temporal_graph`
   and :func:`~networkx_temporal.utils.is_static_graph`
   may also be used to check if an object is an instance of a temporal or
   static NetworkX graph, respectively.
"""

from .typing import (
    Literal,
    Figure,
    StaticGraph,
    TemporalGraph,
)
