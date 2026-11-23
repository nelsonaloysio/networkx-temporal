"""
Algorithms and metrics for temporal graphs.

.. rubric:: Community detection - Summary

.. autosummary::

    leiden_communities
    leiden_communities_temporal
    spectral_clustering
    spectral_clustering_laplacian
    spectral_clustering_bethe_hessian
    spectral_clustering_modularity

.. rubric:: Node metrics - Summary

.. autosummary::

    degree
    in_degree
    out_degree
    degree_centrality
    in_degree_centrality
    out_degree_centrality
    bridging_centrality
    brokering_centrality

.. rubric:: Graph metrics - Summary

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

Setting ``NX_GPU_AUTOCONFIG=1`` in the environment sets ``device='gpu'`` as default on supported
functions. The :attr:`~networkx_temporal.algorithms.is_gpu_enabled` variable allows to check if GPU
acceleration is enabled by default:

.. code-block:: python

    >>> import os
    >>> os.environ["NX_GPU_AUTOCONFIG"] = "1"  # Enable GPU acceleration by default.
    >>>
    >>> import networkx_temporal as tx
    >>> tx.is_gpu_enabled                      # Check whether GPU acceleration is enabled.

    True

A compatible device and the required libraries must be installed for GPU acceleration to work.
See the `GPU acceleration <../examples/gpu.html#accelerating-temporal-graph-algorithms>`_ page
for installation instructions, examples of usage, and result comparisons.

.. rubric:: Functions
"""

from .community import *
from .gpu import NX_GPU_AUTOCONFIG as is_gpu_enabled
from .graph import *
from .node import *

__all__ = (
    "is_gpu_enabled",
    "leiden_communities",
    "leiden_communities_temporal",
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
)
