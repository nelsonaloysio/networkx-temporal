from typing import List, Optional, Union

import numpy as np
try:
    from networkx import to_scipy_sparse_array
except ImportError:
    from networkx import to_scipy_sparse_matrix as to_scipy_sparse_array
import scipy.sparse as sp
try:
    from scipy.sparse import csr_array
except ImportError:
    from scipy.sparse import csr_matrix as csr_array

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph


def spectral_modularity(
    A: Union[np.array, csr_array, StaticGraph],
    communities: Union[np.array, csr_array],
    resolution: Optional[float] = 1,
    directed: Optional[bool] = True,
    weight: Optional[Union[str, bool]] = True,
) -> float:
    """ Calculates modularity using the spectral method.

    Spectral modularity [9]_ computes the value :math:`Q` from an (optionally sparse)
    adjacency matrix :math:`\\mathbf{A}`,

    .. math::

        Q = \\frac{1}{2m} \\mathbf{C}^\\text{T} \\mathbf{B} \\mathbf{C},
        \\quad \\text{with} \\quad
        \\mathbf{B} = \\mathbf{A} - \\gamma
        \\frac{\\mathbf{d_{out}} \\, \\mathbf{d_{in}}^\\text{T}}{2m},

    where
    :math:`\\mathbf{B}` is the modularity matrix,
    :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix
    with :math:`n` as the number of nodes and :math:`k` the number of communities,
    :math:`m` is the total number of edges,
    :math:`\\mathbf{d_{in}}` and :math:`\\mathbf{d_{out}}` are the node in- and out-degree vectors,
    and :math:`\\gamma` is the resolution parameter.

    .. [9] Newman, M. E. J. (2006). ''Modularity and community structure in networks''.
        Proceedings of the National Academy of Sciences, 103(23), 8577-8582.

    :param object A: Adjacency matrix (dense numpy array or sparse scipy matrix).
        If a static NetworkX graph object is provided, its adjacency matrix is used.
    :param communities: Community assignment matrix with shape ``(n_nodes, k_communities)``,
        a or vector of length ``n_nodes``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param directed: Whether the graph is directed. Default is ``True``.
    :param weight: Whether to consider edge weights. If a string is provided,
        it is used as the edge attribute key. Default is ``True``.
    """
    resolution = 1 if resolution is None else resolution
    directed = True if directed is None else directed
    weight = True if weight is None else weight

    if is_static_graph(A):
        A = to_scipy_sparse_array(A,
                                  nodelist=list(A.nodes()),
                                  weight="weight" if weight is True else weight)
    if is_temporal_graph(A):
        raise TypeError(
            "Argument `A` must be a static NetworkX graph, numpy array, or scipy matrix."
        )
    if type(A) not in (np.array, sp.csr_array):
        raise TypeError("Adjacency matrix `A` must be a numpy array or scipy sparse matrix.")

    n_nodes = A.shape[0]
    communities = np.array(communities)
    k_communities = np.unique(communities).shape[0]

    if communities.ndim == 1 and len(communities) != n_nodes:
        raise ValueError(
            "Argument `communities` must match number of nodes or snapshots in the graph."
        )

    if not weight:
        A[A != 0] = 1

    # Degree vectors (optionally corrected) and outer product.
    if directed:
        d_in = A.sum(axis=0)
        d_out = A.sum(axis=1)
    else:
        d_in = d_out = A.sum(axis=0)
    # Apply correction if provided.
    D = d_out.reshape(-1, 1) @ d_in.reshape(1, -1)

    # Community assignment matrix.
    if communities.ndim == 1:
        C = sp.csr_matrix((np.ones(n_nodes), (np.arange(n_nodes), communities)))
    else:
        C = np.zeros((n_nodes, k_communities))
        for c in (communities if type(communities[0]) == list else [communities]):
            C[np.arange(n_nodes), c] += 1

    # Modularity matrix.
    B = A - ((D * resolution) / ((C.T @ A @ C).sum()))

    # Compute modularity.
    Q = np.trace((C.T @ B @ C) / A.sum())

    return float(Q)
