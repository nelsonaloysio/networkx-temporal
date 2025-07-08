"""
Generative models for temporal networks.

.. rubric:: Summary

.. autosummary::

    stochastic_block_model
    generate_block_matrix
    generate_transition_matrix
    generate_degree_vector
    generate_community_vector
    transition_node_memberships
"""

from .sbm import (
    stochastic_block_model,
    generate_block_matrix,
    generate_transition_matrix,
    generate_degree_vector,
    generate_community_vector,
    transition_node_memberships,
)
__all__ = (
    "stochastic_block_model",
    "generate_block_matrix",
    "generate_transition_matrix",
    "generate_degree_vector",
    "generate_community_vector",
    "transition_node_memberships",
)