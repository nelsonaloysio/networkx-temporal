import logging as log
from inspect import signature
from typing import List, Optional, Union
from warnings import warn

from .bethe_hessian import spectral_clustering_bethe_hessian
from .laplacian import spectral_clustering_laplacian
from .modularity import spectral_clustering_modularity
from ...gpu import NX_GPU_AUTOCONFIG
from ....classes import is_static_graph, is_temporal_graph
from ....typing import Literal, StaticGraph, TemporalGraph
from ....utils import to_supra_adjacency_matrix

OPERATOR = Literal["laplacian", "bethe_hessian", "modularity"]
OPERATORS = list(OPERATOR.__args__)

DEVICE = "gpu" if NX_GPU_AUTOCONFIG else "cpu"


def spectral_clustering(
    graph: Union[TemporalGraph, StaticGraph],
    operator: OPERATOR = "laplacian",
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    device: Literal["cpu", "gpu"] = DEVICE,
    **kwargs,
) -> Union[List[int], List[List[int]]]:
    """ Spectral clustering of a temporal or static graph.

    High-level function that dispatches to CPU or GPU devices based on ``device``.
    This function builds the (supra-)adjacency matrix of a static or temporal graph and
    computes its spectral partitions by clustering with :math:`k`-means the leading :math:`k`
    eigenvectors of its specified ``operator``:

    - ``'laplacian'``: normalized or unnormalized matrix with
      :func:`~networkx_temporal.algorithms.spectral_clustering_laplacian`;

    - ``'bethe_hessian'``: Bethe-Hessian matrix with
      :func:`~networkx_temporal.algorithms.spectral_clustering_bethe_hessian`;

    - ``'modularity'``: multislice or static modularity matrix with
      :func:`~networkx_temporal.algorithms.spectral_clustering_modularity`.

    Note that operators accept different keyword arguments; see their documentation for details.

    .. seealso::

        The `Examples → GPU acceleration → Spectral clustering
        <../examples/gpu.html#spectral-clustering>`__ page for examples.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX
        graph object.
    :param str operator: The spectral operator to use. Supported types:
        ``'laplacian'`` (default), ``'bethe_hessian'``, and ``'modularity'``.
    :param weight: Edge attribute to use as weight. If unset, treat edges as unweighted.
    :param interslice_weight: Weight of inter-slice edges connecting node copies across snapshots.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy, SciPy, and scikit-learn.

        - ``'gpu'``: Uses CuPy and cuML (NVIDIA RAPIDS).
          If cuML is not installed, uses CuPy and scikit-learn's :math:`k`-means as fallback.
          Used by default if ``NX_GPU_AUTOCONFIG=1`` is set on the environment on import.

    :param kwargs: Keyword arguments to pass to the backend caller.

    :note: Full GPU aceleration requires cuML on NVIDIA CUDA-enabled hardware.
    """
    if device not in ("cpu", "gpu"):
        raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")

    if (is_static_graph(graph) or is_temporal_graph(graph)) and graph.is_directed():
        raise NotImplementedError("Spectral clustering is not implemented for directed graphs.")

    if operator == "laplacian":
        fnc = spectral_clustering_laplacian
    elif operator == "bethe_hessian":
        fnc = spectral_clustering_bethe_hessian
    elif operator == "modularity":
        fnc = spectral_clustering_modularity
    else:
        raise ValueError(f"Invalid operator: '{operator}' not in {OPERATORS}.")

    sig = signature(fnc)
    fnc_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    fnc_kwargs["device"] = device

    if operator == "modularity":
        fnc_kwargs["offsets"] = kwargs.get(
            "offsets", graph.offsets() if is_temporal_graph(graph) else None
        )

    if any(k not in sig.parameters for k in kwargs):
        invalid_kwargs = set(kwargs) - set(sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for '{fnc.__name__}'. "
            f"Supported keywords are: {set(sig.parameters)}."
        )

    adj, offsets = to_supra_adjacency_matrix(
        graph,
        weight=weight,
        interslice_weight=interslice_weight,
        device=device,
        return_offsets=True,
    )

    assignments = fnc(adj, **fnc_kwargs)

    if is_temporal_graph(graph):
        return [
            assignments[offsets[t]:offsets[t] + len(graph[t])]
            for t in range(len(graph))
        ]

    return assignments


def _resolve_pathway(device):
    """ Resolves ``device`` into ``(xp, xpx, KMeans, eigsh, LinearOperator)``.
    """
    if device == "cpu":
        import numpy as np
        import scipy.sparse as sp
        from scipy.sparse.linalg import eigsh, LinearOperator
        from sklearn.cluster import KMeans  # MiniBatchKMeans as KMeans
        return np, sp, KMeans, eigsh, LinearOperator
    if device == "gpu":
        try:
            # numpy -> cupy, scipy -> cupyx, sklearn -> cuml for GPU acceleration.
            import cupy as cp
            import cupyx.scipy.sparse as cpx
            from cupyx.scipy.sparse.linalg import eigsh, LinearOperator
        except ImportError as exc:
            raise ImportError(
                "Spectral clustering on GPU requires CuPy. Available from: "
                "`conda install -c conda-forge cupy`."
            ) from exc
        try:
            from cuml.cluster import KMeans
        except ImportError:
            warn(
                "Failed to import KMeans from cuml.cluster, falling back to sklearn.cluster (CPU)."
                " Available from: `conda install -c conda-forge -c rapidsai -c nvidia cuml.`",
                ImportWarning
            )
            log.error("ImportError: spectral._resolve_pathway(): from cuml.cluster import KMeans")
        return cp, cpx, KMeans, eigsh, LinearOperator
    raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")
