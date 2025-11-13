from typing import List, Optional, Union

import numpy as np
import scipy.sparse as sp
try:
    from networkx import to_scipy_sparse_array
except ImportError:
    from networkx import to_scipy_sparse_matrix as to_scipy_sparse_array

from ...classes.types import is_static_graph
from ...typing import StaticGraph, TemporalGraph


def spectral_modularity(
    A: Union[np.array, sp.csr_array, StaticGraph, TemporalGraph],
    communities: Union[np.array, sp.csr_array],
    resolution: Optional[float] = 1,
    directed: Optional[bool] = True,
    weight: Optional[Union[str, bool]] = True,
) -> Union[float, List[float]]:
    """ Calculates modularity using the spectral method.

    :param A: Adjacency matrix as a numpy array or scipy sparse matrix,
        or a static NetworkX graph object.
    :param C: Community assignment matrix with shape ``(n_nodes, k_communities)``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param directed: Whether the graph is directed. Default is ``True``.
    :param weight: Whether to consider edge weights. If a string is provided,
        it is used as the edge attribute key. Default is ``True``.
    :param theta: Correction factor for the degree product in the modularity matrix.
        Default is ``None``.
    :param norm: Normalization factor for the modularity matrix. Default is ``1``.
    """
    resolution = 1 if resolution is None else resolution
    directed = True if directed is None else directed
    weight = True if weight is None else weight

    if is_static_graph(A):
        A = to_scipy_sparse_array(A,
                                  nodelist=list(A.nodes()),
                                  weight="weight" if weight is True else weight)

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
