"""
Algorithms and metrics for temporal graphs.

.. rubric:: Community detection - Summary

.. autosummary::

   leiden_communities
   leiden_multislice_gpu
   spectral_clustering
   spectral_clustering_laplacian
   spectral_clustering_bethe_hessian
   spectral_clustering_modularity

.. rubric:: Node-level metrics - Summary

.. autosummary::

   degree
   in_degree
   out_degree
   degree_centrality
   in_degree_centrality
   out_degree_centrality
   bridging_centrality
   brokering_centrality

.. rubric:: Graph-level metrics - Summary

.. autosummary::

   centralization
   degree_centralization
   in_degree_centralization
   out_degree_centralization
   conductance
   modularity
   modularity_multislice
   modularity_spectral

.. rubric:: Note

The convenience function :func:`~networkx_temporal.algorithms.is_gpu_enabled`
may be used to check if GPU acceleration is enabled in the current environment:

.. code-block:: python

   >>> import os
   >>> os.environ["NX_CUGRAPH_AUTOCONFIG"] = "1"  # Enable GPU acceleration by default.
   >>>
   >>> import networkx_temporal as tx
   >>> tx.is_gpu_enabled  # Check whether GPU acceleration is enabled.

   True

.. rubric:: Functions
"""

from .community import *
from .community.leiden.multislice_gpu import leiden_multislice_gpu
from .cugraph import NX_CUGRAPH_AUTOCONFIG
from .graph import *
from .node import *

is_gpu_enabled = NX_CUGRAPH_AUTOCONFIG

__all__ = (
    "leiden_communities",
    "leiden_multislice_gpu",
    "spectral_clustering",
    "spectral_clustering_laplacian",
    "spectral_clustering_bethe_hessian",
    "spectral_clustering_modularity",
    "degree",
    "in_degree",
    "out_degree",
    "degree_centrality",
    "in_degree_centrality",
    "out_degree_centrality",
    "bridging_centrality",
    "brokering_centrality",
    "centralization",
    "degree_centralization",
    "in_degree_centralization",
    "out_degree_centralization",
    "conductance",
    "modularity",
    "modularity_multislice",
    "modularity_spectral",
    "is_gpu_enabled",
)
