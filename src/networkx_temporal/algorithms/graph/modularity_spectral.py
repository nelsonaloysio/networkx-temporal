from typing import Optional, Union

import numpy as np
import scipy.sparse as sp


def modularity_spectral(
    adj: Union[np.ndarray, sp.sparray, sp.spmatrix],
    communities: object,
    gamma: Optional[float] = 1,
    directed: Optional[bool] = True,
    weight: Optional[Union[str, bool]] = True,
) -> float:
    """ Calculates modularity on the graph spectrum. Expects a dense or sparse ``adj``
    matrix from :func:`~networkx_temporal.utils.convert.to_numpy` or
    :func:`~networkx_temporal.utils.convert.to_scipy`, respectively.
    Supports mixed-membership (soft) assignments.

    The spectral modularity [9]_ for a matrix of community assignments :math:`\\mathbf{C}` is
    computed as

    .. math::

        \\mathcal{Q} = \\frac{1}{2m} \\mathbf{C}^\\text{T} \\mathbf{B} \\mathbf{C},
        \\quad \\text{with} \\quad
        \\mathbf{B} = \\mathbf{A} - \\gamma
        \\frac{\\mathbf{d_{out}} \\, \\mathbf{d_{in}}^\\text{T}}{2m},

    where
    :math:`m` is the total number of edges,
    :math:`\\mathbf{A}` is the input adjacency matrix,
    :math:`\\mathbf{B}` is the modularity matrix,
    :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix
    with :math:`n` as the number of nodes and :math:`k` the number of communities,
    :math:`\\mathbf{d_{in}}` and :math:`\\mathbf{d_{out}}` are the node in- and out-degree vectors,
    and :math:`\\gamma = 1` (default) is the resolution parameter, where larger values lead to
    smaller communities.

    .. [9] Newman, M. E. J. (2006). ''Modularity and community structure in networks''.
        Proceedings of the National Academy of Sciences, 103(23), 8577-8582.

    :param adj: Adjacency matrix in CSR format. Accepts dense (NumPy) or sparse (SciPy) matrices.
    :param communities: Community assignment matrix with shape ``(n_nodes, k_communities)``,
        a or vector of length ``n_nodes``.
    :param gamma: The resolution parameter. Default is ``1``.
    :param directed: Whether the graph is directed. Default is ``True``.
    :param weight: Whether to consider edge weights. If a string is provided,
        it is used as the edge attribute key. Default is ``True``.
    """
    if type(adj) not in (np.ndarray, sp.sparray, sp.spmatrix):
        raise TypeError(
            f"Expected a dense or sparse adjacency matrix, got {type(adj)}."
        )

    gamma = 1 if gamma is None else gamma
    directed = True if directed is None else directed
    weight = True if weight is None else weight

    n_nodes = adj.shape[0]
    communities = np.array(communities)
    k_communities = np.unique(communities).shape[0]

    if not weight:
        adj[adj != 0] = 1

    # Degree vectors (optionally corrected) and outer product.
    if directed:
        d_in = adj.sum(axis=0)
        d_out = adj.sum(axis=1)
    else:
        d_in = d_out = adj.sum(axis=0)
    # Apply correction if provided.
    D = d_out.reshape(-1, 1) @ d_in.reshape(1, -1)

    # Community assignment matrix.
    if communities.ndim == 2:
        C = communities
    elif communities.ndim == 1:
        C = sp.csr_matrix((np.ones(n_nodes), (np.arange(n_nodes), communities)))
    else:
        C = np.zeros((n_nodes, k_communities))
        for c in (communities if type(communities[0]) == list else [communities]):
            C[np.arange(n_nodes), c] += 1

    # Modularity matrix.
    B = adj - ((D * ggama) / ((C.T @ adj @ C).sum()))

    # Compute modularity.
    Q = np.trace((C.T @ B @ C) / adj.sum())

    return float(Q)
