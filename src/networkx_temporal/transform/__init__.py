"""
Transform data between different temporal graph representations.

.. rubric:: Summary

.. autosummary::

   from_events
   from_snapshots
   from_static
   from_unrolled
   to_events
   to_snapshots
   to_static
   to_unrolled

.. rubric:: Functions
"""

from .events import from_events, to_events
from .snapshots import from_snapshots, to_snapshots
from .static import from_static, to_static
from .unrolled import from_unrolled, to_unrolled

__all__ = (
    "from_events",
    "from_snapshots",
    "from_static",
    "from_unrolled",
    "to_events",
    "to_snapshots",
    "to_static",
    "to_unrolled",
)