"""
.. rubric:: Functions - Community metrics
"""

from .modularity import (
    modularity,
    longitudinal_modularity,
    multislice_modularity,
)

__all__ = (
    "modularity",
    "longitudinal_modularity",
    "multislice_modularity",
)