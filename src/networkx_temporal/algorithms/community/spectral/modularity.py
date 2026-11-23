from typing import List, Optional

import scipy.sparse as sp

from ...gpu import NX_GPU_AUTOCONFIG
from ....typing import Literal

DEVICE = "gpu" if NX_GPU_AUTOCONFIG else "cpu"


def spectral_clustering_modularity(
    adj: sp.spmatrix,
    k: int,
    offsets: Optional[List[int]] = None,
    gamma: float = 1.0,
    n_init: int = 10,
    max_iter: int = 300,
    seed: Optional[int] = None,
    device: Literal["cpu", "gpu"] = DEVICE
) -> List[int]:
    """ Spectral clustering via the modularity operator.
    Also available via :func:`~networkx_temporal.algorithms.spectral_clustering`.

    Given a (supra-)adjacency matrix, computes the eigenvectors associated with the :math:`k`
    largest eigenvalues of the (supra-)modularity matrix and clusters the resulting embedding with
    :math:`k`-means. This is a spectral relaxation of
    :func:`~networkx_temporal.algorithms.modularity_multislice` maximization, that is,

    .. math::

        \\mathcal{Q}_\\mathrm{MS} =
        \\frac{1}{2 \\mu}
        \\mathrm{Tr} (\\mathbf{C}^\\top \\mathbf{M} \\mathbf{C}),

    where :math:`\\mathbf{C}` is the (binary) community assignment matrix,
    :math:`\\mu` is the total intra- and inter-layer edge weight in the temporal graph,
    and :math:`\\mathbf{M}` is the (supra-)modularity matrix, with diagonal blocks

    .. math::

        \\mathbf{B}^{(t)} =
        \\mathbf{A}^{(t)} - \\gamma \\frac{\\mathbf{d}^{(t)} \\mathbf{d}^{(t)\\top}}{2 m^{(t)}}

    and off-diagonal blocks :math:`\\omega^{(sr)} \\mathbf{I}` coupling temporal node copies,
    :math:`\\mathbf{A}^{(t)}` is the adjacency
    matrix of snapshot :math:`t`, :math:`\\mathbf{d}^{(t)}` its degree vector,
    :math:`m^{(t)}` its total edge weight, and :math:`\\gamma` the resolution parameter.

    Relaxing :math:`\\mathbf{C}` to a real-valued matrix with orthonormal columns, the trace is
    maximized by the leading :math:`k` eigenvectors of :math:`\\mathbf{M}`. Rows of the embedding
    are rescaled to unit :math:`\\ell_2`-norm before clustering [1]_.
    The null model is applied implicitly as a linear operator to avoid materializing
    :math:`\\mathbf{M}` as a dense matrix. Requires ``adj`` to be symmetric (undirected graph)
    and specifying the number of communities ``k`` in advance. Reduces to
    :func:`~networkx_temporal.algorithms.modularity` maximization if ``offsets`` is unset.

    :param adj: Adjacency or supra-adjacency matrix in CSR format.
        Accepts dense NumPy (CPU) or sparse SciPy/CuPy (GPU) matrices.
    :param k: Number of communities or number of eigenvectors computed.
    :param offsets: List of starting node indices for each snapshot in the graph.
        Obtained by :func:`~networkx_temporal.classes.TemporalGraph.offsets`, or
        :func:`~networkx_temporal.utils.to_supra_adjacency_matrix` with
        ``return_offsets=True``. Required for multislice modularity maximization.
    :param gamma: Resolution parameter :math:`\\gamma`. Default is ``1.0``.
        Controls the size of communities, where higher values lead to smaller communities.
    :param n_init: Number of random initializations for :math:`k`-means.
    :param max_iter: Maximum number of iterations for :math:`k`-means.
    :param seed: Random seed for :math:`k`-means.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy, SciPy, and scikit-learn.

        - ``'gpu'``: Uses CuPy and cuML (NVIDIA RAPIDS).
          If cuML is not installed, uses CuPy and scikit-learn's :math:`k`-means as fallback.
          Used by default if ``NX_GPU_AUTOCONFIG=1`` is set on the environment on import.

    :note: Full GPU acceleration requires cuML on NVIDIA CUDA-enabled hardware.
    """
    from .spectral import _resolve_pathway
    xp, _, KMeans, eigsh, LinearOperator = _resolve_pathway(device)

    if offsets is None:
        offsets = [0]
    T = len(offsets)

    n_t = [offsets[t + 1] - offsets[t] for t in range(T - 1)] + [adj.shape[0] - offsets[-1]]
    n_nodes = sum(n_t)

    # Recover intra-slice degrees and edge counts from diagonal blocks only,
    # excluding inter-slice couplings (which live in off-diagonal blocks).
    d, m = [], []
    for t in range(T):
        s = offsets[t]
        e = s + n_t[t]
        A_block = adj[s:e, s:e] # intra-slice block A^(t)
        d_t = xp.asarray(A_block.sum(axis=1)).ravel().astype(xp.float32)
        m_t = float(A_block.sum()) / 2.0
        d.append(d_t)
        m.append(max(m_t, 1e-12))

    # Matrix-vector product.
    def _matvec(v):
        v = v.ravel().astype(xp.float32)
        result = (adj @ v).ravel() # full supra-adjacency term
        for t in range(T):
            sl = slice(offsets[t], offsets[t] + n_t[t])
            # Rank-1 correction: -γ d_t (d_t^T v_t) / (2 m_t)
            result[sl] -= (gamma / (2.0 * m[t])) * d[t] * (d[t] @ v[sl])
        return result

    # M @ v  =  A_supra @ v  -  γ Σ_t  d_t (d_t^T v_t) / (2 m_t)
    # NOTE: null model is block-diagonal of rank-1 outer products d_t d_t^T,
    # but we apply it implicitly via dot products O(N) to avoid O(N²) per
    # eigsh iteration from explicit construction of the dense null model.
    M_op = LinearOperator(
        shape=(n_nodes, n_nodes),
        matvec=_matvec,
        dtype=xp.float32,
    )

    # Compute k leading eigenvectors of M (symmetric eigsh);
    # "LA" selects the k largest algebraic eigenvalues, where positive
    # eigenvalues correspond to modularity-increasing community structure.
    _eigenvalues, U = eigsh(M_op, k=k, which="LA")
    # NOTE: eigsh returns columns in ascending order; reverse so index 0 is dominant.
    U = U[:, ::-1]  # [n_nodes, k]

    # L2-normalize rows and perform k-means clustering on GPU.
    # Row normalization (Ng et al. 2002) improves k-means stability by
    # mapping the eigenvector embedding onto the unit hypersphere.
    norms = xp.linalg.norm(U, axis=1, keepdims=True)
    norms = xp.where(norms < xp.float32(1e-10), xp.float32(1.0), norms)
    U = U / norms

    km = KMeans(n_clusters=k, random_state=seed, n_init=n_init, max_iter=max_iter)
    labels_gpu = km.fit_predict(U.astype(xp.float32, copy=False))
    labels = xp.asarray(labels_gpu).astype(int, copy=False)
    return labels.tolist()
