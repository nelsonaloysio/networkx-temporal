"""
Generative models for temporal networks.

.. rubric:: Summary

.. autosummary::

   sbm.sbm_dynamic
   sbm.generate_block_matrix
   sbm.generate_transition_matrix
   sbm.generate_degree_vector
   sbm.generate_community_vector
"""

from .sbm import (
    sbm_dynamic,
    generate_block_matrix,
    generate_transition_matrix,
    generate_degree_vector,
    generate_community_vector,
)

__all__ = ("sbm_dynamic",)