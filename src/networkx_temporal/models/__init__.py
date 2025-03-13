"""
Generative models for temporal networks.

.. rubric:: Summary

.. autosummary::

   dynamic_sbm
   block_matrix
   transition_matrix
   degree_vector
   community_vector

.. rubric:: Functions
"""

from .sbm import (
    dynamic_sbm,
    block_matrix,
    transition_matrix,
    degree_vector,
    community_vector,
)

__all__ = (
    "dynamic_sbm",
)