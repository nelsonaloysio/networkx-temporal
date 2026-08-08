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

The property :mod:`~networkx_temporal.algorithms.is_gpu_enabled`
allows checking if GPU acceleration is enabled in the environment:

.. code-block:: python

   >>> import os
   >>> os.environ["NX_CUGRAPH_AUTOCONFIG"] = "1"  # Enable GPU acceleration by default.
   >>>
   >>> import networkx_temporal as tx
   >>> tx.is_gpu_enabled  # Check whether GPU acceleration is enabled.

   True

Note that a compatible GPU device and the required libraries must be installed for GPU acceleration
to work. See the `GPU acceleration <../examples/gpu.html#accelerating-temporal-graph-algorithms>`__
page for more details.

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
