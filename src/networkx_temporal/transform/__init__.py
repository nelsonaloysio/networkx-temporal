"""
Transform data between different temporal graph representations.

.. rubric:: Summary

.. autosummary::

   from_events
   from_snapshots
   from_static
   from_unified
   to_events
   to_snapshots
   to_static
   to_unified

.. rubric:: Functions
"""

from .events import from_events, to_events
from .snapshots import from_snapshots, to_snapshots
from .static import from_static, to_static
from .unified import from_unified, to_unified

__all__ = (
    "from_events",
    "from_snapshots",
    "from_static",
    "from_unified",
    "to_events",
    "to_snapshots",
    "to_static",
    "to_unified",
)