"""
Generative models for temporal networks.

.. rubric:: Summary - Models

.. autosummary::

    dynamic_stochastic_block_model
    stochastic_block_model

.. rubric:: Summary - Datasets

.. autosummary::

    collegemsg_graph
    example_sbm_graph
    pubmed_graph

.. rubric:: Summary - Utilities

.. autosummary::

    generate_block_matrix
    generate_community_matrix
    generate_community_vector
    generate_degree_vector
    generate_transition_matrix
    transition_node_memberships
"""

from .datasets import (
    collegemsg_graph,
    example_sbm_graph,
    pubmed_graph,
)
from .generators import (
    generate_block_matrix,
    generate_community_matrix,
    generate_community_vector,
    generate_degree_vector,
    generate_transition_matrix,
    transition_node_memberships,
)
from .sbm import (
    dynamic_stochastic_block_model,
    stochastic_block_model
)
dynamic_sbm = dynamic_stochastic_block_model  # Alias

__all__ = (
    "dynamic_stochastic_block_model",
    "stochastic_block_model",
    "collegemsg_graph",
    "example_sbm_graph",
    "pubmed_graph",
    "generate_block_matrix",
    "generate_community_matrix",
    "generate_community_vector",
    "generate_degree_vector",
    "generate_transition_matrix",
    "transition_node_memberships",
)
