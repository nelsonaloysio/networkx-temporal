"""
Input/Output functions for temporal graphs.

.. autosummary::

   read_graph
   read_hif
   write_graph

.. rubric:: Functions
"""

from .hif import read_hif
from .reader import read_graph
from .writer import write_graph

__all__ = (
    "read_graph",
    "read_hif",
    "write_graph",
)