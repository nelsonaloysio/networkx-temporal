"""
Generative models for temporal networks.

.. rubric:: Summary - Models

.. autosummary::

    dynamic_stochastic_block_model
    stochastic_block_model

.. rubric:: Summary - Dataset loaders

.. autosummary::

    collegemsg_graph
    example_sbm_graph
    fediverse_graph
    pubmed_graph
    travian_graph

.. rubric:: Summary - Utilities

.. autosummary::

    community_matrix_from_vector
    generate_block_matrix
    generate_community_matrix
    generate_community_vector
    generate_degree_vector
    generate_transition_matrix
    transition_node_memberships

.. rubric:: Functions
"""

from .datasets import (
    collegemsg_graph,
    fediverse_graph,
    pubmed_graph,
    travian_graph,
)
from .examples import (
    example_sbm_graph,
)
from .generators import (
    community_matrix_from_vector,
    generate_block_matrix,
    generate_community_matrix,
    generate_community_vector,
    generate_degree_vector,
    generate_transition_matrix,
    transition_node_memberships,
)
from .sbm import (
    dynamic_sbm,
    dynamic_stochastic_block_model,
    stochastic_block_model
)

__all__ = (
    "dynamic_sbm",
    "dynamic_stochastic_block_model",
    "stochastic_block_model",
    "collegemsg_graph",
    "fediverse_graph",
    "pubmed_graph",
    "travian_graph",
    "example_sbm_graph",
    "community_matrix_from_vector",
    "generate_block_matrix",
    "generate_community_matrix",
    "generate_community_vector",
    "generate_degree_vector",
    "generate_transition_matrix",
    "transition_node_memberships",
)
