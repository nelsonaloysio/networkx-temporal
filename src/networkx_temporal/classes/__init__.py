"""
Classes and functions for temporal graph objects.

.. rubric:: Classes - Summary

.. autosummary::

    TemporalGraph
    TemporalDiGraph
    TemporalMultiGraph
    TemporalMultiDiGraph
    TemporalABC

.. rubric:: Functions - Summary

.. autosummary::

    temporal_graph
    empty_graph
    all_neighbors
    compose
    compose_all
    edge_subgraph
    from_multigraph
    is_events_graph
    is_events_multigraph
    is_frozen
    is_static_graph
    is_temporal_graph
    is_unrolled_graph
    isolates
    neighbors
    relabel_nodes
    subgraph
    to_multigraph

.. rubric:: Classes

.. autoclass:: networkx_temporal.classes.TemporalGraph
    :members:
    :inherited-members: Graph

.. autoclass:: networkx_temporal.classes.TemporalDiGraph
    :members:

.. autoclass:: networkx_temporal.classes.TemporalMultiGraph
    :members:

.. autoclass:: networkx_temporal.classes.TemporalMultiDiGraph
    :members:

.. autoclass:: TemporalABC

.. rubric:: Functions
"""

from .abc import TemporalABC
from .digraph import TemporalDiGraph
from .factory import temporal_graph, empty_graph
from .functions import (
    all_neighbors,
    compose,
    compose_all,
    create_empty_copy,
    edge_subgraph,
    from_multigraph,
    isolates,
    neighbors,
    relabel_nodes,
    subgraph,
    to_multigraph,
    set_edge_attributes,
    set_node_attributes,
)
from .graph import TemporalGraph
from .multidigraph import TemporalMultiDiGraph
from .multigraph import TemporalMultiGraph
from .types import (
    is_events_graph,
    is_events_multigraph,
    is_frozen,
    is_static_graph,
    is_temporal_graph,
    is_unrolled_graph,
)

__all__ = (
    "TemporalGraph",
    "TemporalDiGraph",
    "TemporalMultiGraph",
    "TemporalMultiDiGraph",
    "TemporalABC",
    "temporal_graph",
    "empty_graph",
    "all_neighbors",
    "compose",
    "compose_all",
    "create_empty_copy",
    "edge_subgraph",
    "from_multigraph",
    "is_events_graph",
    "is_events_multigraph",
    "is_frozen",
    "is_static_graph",
    "is_temporal_graph",
    "is_unrolled_graph",
    "isolates",
    "neighbors",
    "relabel_nodes",
    "set_edge_attributes",
    "set_node_attributes",
    "subgraph",
    "to_multigraph",
)