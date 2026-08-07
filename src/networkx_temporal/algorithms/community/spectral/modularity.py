from typing import List, Optional, Union

import scipy.sparse as sp

from ...cugraph import NX_CUGRAPH_AUTOCONFIG
from ....typing import Literal

DEVICE = "gpu" if NX_CUGRAPH_AUTOCONFIG else "cpu"


def spectral_clustering_modularity(
    adj: Union[sp.sparray, sp.spmatrix],
    k: int,
    offsets: Optional[List[int]] = None,
    gamma: float = 1.0,
    n_init: int = 10,
    max_iter: int = 300,
    seed: Optional[int] = None,
    device: Literal["cpu", "gpu"] = DEVICE
) -> List[dict]:
    """ Spectral clustering via  multislice modularity.

    Multislice modularity (Mucha et al. 2010) generalizes the Newman-Girvan modularity to
    temporal graphs by introducing inter-slice couplings between node copies across snapshots,

    .. math::

       \\mathcal{Q}_\\mathrm{MS} =
       (\\frac{1}{2 \\mu})
       \\mathrm{Tr} (\\mathbf{C}^\\top \\mathbf{M} \\mathbf{C})

    where :math:`\\mathbf{M}` is the supra-modularity matrix with diagonal blocks
    :math:`\\mathbf{B}^{(t)} = \\mathbf{A}^{(t)} - \\gamma \\frac{d^{(t)} d^{(t)T}}{2 m^{(t)}}`
    and off-diagonal blocks :math:`\\omega^{(sr)} \\mathbf{I}` connecting nodes across
    snapshots, and :math:`\\mathbf{C}` is the community matrix.

    This function computes the leading :math:`k` eigenvectors of the supra-modularity matrix and
    clusters them via :math:`k`-means to produce a temporal community assignment. Note that GPU
    eigensolvers require :math:`\\mathbf{M}` to be be symmetric, so only undirected graphs are
    currently supported.

    .. hint::

       Setting ``NX_CUGRAPH_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    .. seealso::

       The :func:`~networkx_temporal.algorithms.community.spectral.spectral_clustering`
       function for a convenience wrapper around this function.

    :param adj: Adjacency or supra-adjacency matrix in CSR format.
        Accepts dense NumPy (CPU) or sparse SciPy/CuPy (GPU) matrices.
    :param k: Number of communities.
    :param offsets: List of starting indices for each snapshot in the supra-adjacency matrix.
        Obtained by :func:`~networkx_temporal.classes.TemporalGraph.offsets`, or
        :func:`~networkx_temporal.utils.temporal.to_supra_adjacency_matrix` with
        ``return_offsets=True``. If ``None``, assumes a static graph.
    :param gamma: Resolution parameter :math:`\\gamma` (default: ``1.0``). Controls the size of the
        communities found, where higher values lead to smaller communities.
    :param n_init: Number of random initializations for :math:`k`-means.
    :param max_iter: Maximum number of iterations for :math:`k`-means.
    :param seed: Random seed for :math:`k`-means.
    :param str device: Whether to run on ``'cpu'`` (defalult) or ``'gpu'``.

    :note: GPU acceleration requires the CuPy and RAPIDS cuML libraries.
    """
    if device == "cpu":
        import numpy as xp
        import scipy.sparse as xsp
        from sklearn.cluster import KMeans
        from scipy.sparse.linalg import eigsh, LinearOperator
    elif device == "gpu":
        try:
            # Override numpy -> cupy, scipy -> cupyx, sklearn -> cuml for GPU acceleration.
            import cupy as xp
            import cupyx.scipy.sparse as xsp
            from cuml.cluster import KMeans
            from cupyx.scipy.sparse.linalg import eigsh, LinearOperator
        except ImportError as exc:
            raise ImportError(
                "GPU spectral clustering requires CuPy and CuML. Please install it via"
                " `conda install -c conda-forge -c rapidsai -c nvidia cupy cuml`."
            ) from exc
    else:
        raise ValueError(f"Invalid device '{device}'. Supported devices are: 'cpu', 'gpu'.")

    if offsets is None:
        T = 1
        offsets = [0, adj.shape[0]]
    else:
        T = len(offsets) - 1

    n_t = [offsets[t + 1] - offsets[t] for t in range(T)] + [adj.shape[0] - offsets[-1]]
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

    def _matvec(v):
        v = v.ravel().astype(xp.float32)
        result = (adj @ v).ravel() # full supra-adjacency term
        for t in range(T):
            sl = slice(offsets[t], offsets[t] + n_t[t])
            # Rank-1 correction: -γ d_t (d_t^T v_t) / (2 m_t)
            result[sl] -= (gamma / (2.0 * m[t])) * d[t] * (d[t] @ v[sl])
        return result

    # LinearOperator for M (avoids materialising dense null model):
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
