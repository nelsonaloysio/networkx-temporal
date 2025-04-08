"""
Algorithms and metrics for temporal graphs.

.. rubric:: Summary - Graphs

.. autosummary::

   centralization
   degree_centralization
   in_degree_centralization
   out_degree_centralization
   modularity
   multislice_modularity
   longitudinal_modularity

.. rubric:: Summary - Nodes

.. autosummary::

   degree
   in_degree
   out_degree
   degree_centrality
   in_degree_centrality
   out_degree_centrality
   bridging_centrality
   bridging_coefficient
   brokering_centrality
   clustering_coefficient

.. rubric:: Functions
"""

from .bridging import (
    bridging_centrality,
    bridging_coefficient,
)
from .brokering import (
    brokering_centrality,
    clustering_coefficient,
)
from .centrality import (
    degree_centrality,
    in_degree_centrality,
    out_degree_centrality,
)
from .centralization import (
    centralization,
    degree_centralization,
    in_degree_centralization,
    out_degree_centralization,
)
from .degree import (
    degree,
    in_degree,
    out_degree,
)
from .modularity import (
    modularity,
    multislice_modularity,
    longitudinal_modularity,
)

__all__ = (
    "centralization",
    "degree_centralization",
    "in_degree_centralization",
    "out_degree_centralization",
    "modularity",
    "multislice_modularity",
    "longitudinal_modularity",
    "degree",
    "in_degree",
    "out_degree",
    "degree_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
    "bridging_centrality",
    "bridging_coefficient",
    "brokering_centrality",
    "clustering_coefficient",
)