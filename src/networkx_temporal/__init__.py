"""
Top-level module for the package.

.. rubric:: Summary

.. autosummary::

   drawing
   graph
   io
   metrics
   transform
   typing
   utils

.. rubric:: Note

Some classes and functions are exposed at the top level for convenience and may also be accessed via the
individual modules. For example, the :class:`~networkx_temporal.graph.TemporalGraph` class
can be imported by running:

.. code-block:: python

    >>> from networkx_temporal import TemporalGraph

Or, alternatively, from the :mod:`~networkx_temporal.graph` module in which it is defined:

.. code-block:: python

    >>> from networkx_temporal.graph import TemporalGraph

For detailed information on each class and function, please refer to the individual modules.
"""

from .__version__ import __version__
from .drawing import *
from .graph import *
from .io import *
from .transform import *
from .utils import *
from .utils.convert import *

__all__ = (
    "TemporalGraph",
    "TemporalDiGraph",
    "TemporalMultiGraph",
    "TemporalMultiDiGraph",
    "convert",
    "draw",
    "from_events",
    "from_multigraph",
    "from_snapshots",
    "from_static",
    "from_unified",
    "is_frozen",
    "is_static_graph",
    "is_temporal_graph",
    "read_graph",
    "temporal_graph",
    "to_multigraph",
    "write_graph",
)