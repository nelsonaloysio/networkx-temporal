"""
Input/Output functions for temporal graphs.

.. rubric:: Summary - Graph I/O Functions

.. autosummary::

   read_graph
   write_graph

.. rubric:: Functions
"""

from .reader import read_graph
from .writer import write_graph

__all__ = (
    "read_graph",
    "write_graph",
)