import scipy.sparse as sp
from typing import List, Optional, Union

from ...cugraph import NX_CUGRAPH_AUTOCONFIG
from ....typing import Literal

DEVICE = "gpu" if NX_CUGRAPH_AUTOCONFIG else "cpu"


def spectral_clustering_laplacian(
    adj: Union[sp.sparray, sp.spmatrix],
    k: Optional[int] = None,
    normalized: bool = True,
    n_init: int = 10,
    max_iter: int = 300,
    seed: Optional[int] = None,
    device: Literal["cpu", "gpu"] = DEVICE,
) -> List[int]:
    """ Spectral clustering via the Laplacian operator.

    Given a (supra-)adjacency matrix, computes the :math:`k` smallest eigenpairs of the
    graph Laplacian and clusters the resulting embedding with :math:`k`-means. With
    ``normalized=True`` (default), is is symmetric,

    .. math::

        \\tilde{L} =
        \\mathbf{D}^{-1/2} \\mathbf{L} \\mathbf{D}^{-1/2} =
        \\mathbf{I} - \\mathbf{D}^{-1/2} \\mathbf{A} \\mathbf{D}^{-1/2},

    where :math:`\\mathbf{L} = \\mathbf{D} - \\mathbf{A}`,
    :math:`\\mathbf{A}` is the adjacency matrix,
    and :math:`\\mathbf{D}` is the diagonal degree matrix.
    If ``normalized=False``, the unnormalized Laplacian
    :math:`\\mathbf{L} = \\mathbf{D} - \\mathbf{A}` is used instead.

    The number of communities :math:`k` must be provided; the eigenvectors with smallest
    eigenvalues form the node embedding. For the symmetric normalized Laplacian, rows are also
    :math:`L_2`-normalized before clustering (Ng et al., 2002) to correct for the
    :math:`D^{1/2}` scaling.

    Unlike the Bethe-Hessian, the Laplacian degrades near the community detectability threshold on
    sparse graphs. Note that its construction is equivalent to the Bethe-Hessian with :math:`r = 1`.

    .. hint::

       Setting ``NX_CUGRAPH_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    .. seealso::

       The :func:`~networkx_temporal.algorithms.spectral_clustering`
       function for a convenience wrapper around this implementation.

    :param adj: Adjacency or supra-adjacency matrix in CSR format.
        Accepts dense NumPy (CPU) or sparse SciPy/CuPy (GPU) matrices.
    :param k: Number of communities. If unset, estimate from the number of negative eigenvalues.
    :param normalized: Whether to use the normalized Laplacian construction.
    :param max_k: Maximum number of eigenpairs to compute when ``k`` is None.
    :param negative_tol: Tolerance for counting negative eigenvalues when ``k`` is None.
    :param n_init: Number of random initializations for :math:`k`-means.
    :param max_iter: Maximum number of iterations for :math:`k`-means.
    :param seed: Random seed for :math:`k`-means.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy, SciPy, and scikit-learn (default).

        - ``'gpu'``: Uses CuPy, CuPy sparse, and cuML (RAPIDS).

    :note: GPU acceleration requires NVIDIA CUDA-enabled hardware.
    """
    if device == "cpu":
        import numpy as xp
        import scipy.sparse as xsp
        from sklearn.cluster import KMeans
        from scipy.sparse.linalg import eigsh
    elif device == "gpu":
        # Override numpy -> cupy, scipy -> cupyx, sklearn -> cuml for GPU acceleration.
        try:
            import cupy as xp
            import cupyx.scipy.sparse as xsp
            from cuml.cluster import KMeans
            from cupyx.scipy.sparse.linalg import eigsh
        except ImportError as exc:
            raise ImportError(
                "GPU spectral clustering requires CuPy and CuML. Please install it via"
                " `conda install -c conda-forge -c rapidsai -c nvidia cupy cuml`."
            ) from exc
    else:
        raise ValueError(f"Invalid device '{device}'. Supported devices are: 'cpu', 'gpu'.")

    n_nodes = adj.shape[0]
    if n_nodes == 0:
        return []
    if k is None or k < 1:
        raise ValueError("Number of clusters `k` must be a positive integer when provided.")
    if k > n_nodes:
        raise ValueError(f"Number of clusters `k` exceeds number of nodes ({n_nodes}).")

    # Degree vector and diagonal degree matrix.
    degrees = xp.asarray(adj.sum(axis=1)).ravel().astype(xp.float32)
    D = xsp.diags(degrees, offsets=0, format="csr", dtype=xp.float32)

    # Laplacian L = D - A; normalized variant L_sym = I - D^{-1/2} A D^{-1/2}.
    L = D - adj
    if normalized:
        mask = degrees > 0
        d_inv_sqrt = xp.zeros_like(degrees)
        d_inv_sqrt[mask] = 1.0 / xp.sqrt(degrees[mask])
        d_inv_sqrt = d_inv_sqrt.astype(xp.float32)
        D_inv_sqrt = xsp.diags(
            d_inv_sqrt, offsets=0, format="csr", dtype=xp.float32)
        L = D_inv_sqrt @ L @ D_inv_sqrt

    # The k smallest-algebraic eigenpairs give the low-dimensional embedding.
    _eigenvalues, U = eigsh(L.astype(xp.float32), k=k, which="SA")

    # For the symmetric normalized Laplacian, row-normalize the embedding
    # (Ng et al., 2002) to correct for the D^{1/2} scaling before k-means.
    if normalized:
        norms = xp.linalg.norm(U, axis=1, keepdims=True)
        norms = xp.where(norms < xp.float32(1e-10), xp.float32(1.0), norms)
        U = U / norms

    km = KMeans(n_clusters=k, random_state=seed, n_init=n_init, max_iter=max_iter)
    labels = km.fit_predict(U.astype(xp.float32, copy=False))
    labels = xp.asarray(labels).astype(int, copy=False)
    return labels.tolist()
