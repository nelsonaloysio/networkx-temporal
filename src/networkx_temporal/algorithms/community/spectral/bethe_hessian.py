import logging as log
import scipy.sparse as sp
from typing import List, Optional, Union
from warnings import warn

from ...cugraph import NX_CUGRAPH_AUTOCONFIG
from ....typing import Literal

DEVICE = "gpu" if NX_CUGRAPH_AUTOCONFIG else "cpu"


def spectral_clustering_bethe_hessian(
    adj: Union[sp.sparray, sp.spmatrix],
    k: Optional[int] = None,
    r: Optional[float] = None,
    max_k: int = 64,
    negative_tol: float = 1e-7,
    n_init: int = 10,
    max_iter: int = 300,
    seed: Optional[int] = None,
    device: Literal["cpu", "gpu"] = DEVICE,
) -> List[int]:
    """ Spectral clustering via the Bethe-Hessian operator.

    Given a (supra-)adjacency matrix, constructs the Bethe-Hessian matrix

    .. math::

        \\mathbf{H}(r) = (r^2 - 1)\\mathbf{I} - r\\mathbf{A} + \\mathbf{D},

    where :math:`\\mathbf{A}` is the (supra-)adjacency matrix and :math:`\\mathbf{D}` is the
    diagonal (supra-)degree matrix, and computes its smallest algebraic eigenpairs. If ``k`` is
    provided, the corresponding eigenvectors are clustered with cuML :math:`k`-means. If omitted,
    the number of communities is estimated as the number of negative Bethe-Hessian eigenvalues
    among the computed eigenpairs.

    The regularizer parameter ``r``, if unset, is estimated from the graph's
    degree distribution as :math:`r = \\sqrt{\\langle d^2 \\rangle / \\langle d \\rangle - 1}`,
    which is the non-backtracking spectral radius and accounts for degree heterogeneity; it
    approximates :math:`\\sqrt{d}` for near-regular graphs, where :math:`d` is the mean degree.

    Asymptotically, the number of negative Bethe-Hessian eigenvalues estimates the number of
    communities and attains the information-theoretic detectability threshold on sparse SBM
    graphs. Note that this guarantee only holds for unweighted graphs; for weighted graphs,
    the same estimation is employed, but is considered a heuristic approximation instead.

    The sign of ``r`` should be positive for assortative communities and negative for
    disassortative communities; currently estimation only supports assortative structures.

    .. hint::

       Setting ``NX_CUGRAPH_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    .. seealso::

       The :func:`~networkx_temporal.algorithms.community.spectral.spectral_clustering`
       function for a convenience wrapper around this function.

    :param adj: Adjacency or supra-adjacency matrix in CSR format.
        Accepts dense NumPy (CPU) or sparse SciPy/CuPy (GPU) matrices.
    :param k: Number of communities. If unset, estimate from the number of negative eigenvalues.
    :param r: Regularizer parameter. If unset, estimate from the graph's degree distribution.
    :param max_k: Maximum number of eigenpairs to compute when ``k`` is None.
    :param negative_tol: Tolerance for counting negative eigenvalues when ``k`` is None.
    :param n_init: Number of random initializations for :math:`k`-means.
    :param max_iter: Maximum number of iterations for :math:`k`-means.
    :param seed: Random seed for :math:`k`-means.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy, SciPy, and scikit-learn (default).

        - ``'gpu'``: Uses CuPy, CuPy sparse, and RAPIDS cuML (NVIDIA).
    """
    if device == "cpu":
        import numpy as xp
        import scipy.sparse as xsp
        from sklearn.cluster import KMeans
        from scipy.sparse.linalg import eigsh
    elif device == "gpu":
        try:
            # Override numpy -> cupy, scipy -> cupyx, sklearn -> cuml for GPU acceleration.
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
    if k is not None and k < 1:
        raise ValueError("Number of clusters `k` must be a positive integer when provided.")
    if k is not None and k > n_nodes:
        raise ValueError(f"Number of clusters `k` exceeds number of nodes ({n_nodes}).")
    if max_k < 1:
        raise ValueError("Maximum number of clusters `max_k` must be a positive integer.")

    # Estimate `r` from non-backtracking spectral radius r = sqrt(<d^2>/<d> - 1).
    degrees = xp.asarray(adj.sum(axis=1)).ravel().astype(xp.float32)
    if r is None:
        mean_d = float(degrees.mean().item())
        mean_d2 = float((degrees ** 2).mean().item())
        if mean_d <= 1e-12:
            raise ValueError("Mean graph degree is (near) zero; unable to estimate `r`.")
        r_squared = (mean_d2 / mean_d) - 1.0
        if r_squared <= 0:
            # Degenerate (near-regular/very sparse); fall back to sqrt(mean degree).
            r_value = float(xp.sqrt(mean_d))
        else:
            r_value = float(xp.sqrt(r_squared))
        log.info("Estimated `r` from degree distribution: %s", r_value)
    else:
        r_value = float(r)

    if r_value <= 0:
        raise ValueError(f"Regularizer parameter `r` must be positive, got {r_value}.")

    # Construct Bethe-Hessian matrix: H(r) = (r^2 - 1)I - rA + D.
    diagonal = degrees + xp.float32(r_value ** 2 - 1.0)
    H = xsp.diags(diagonal, offsets=0, format="csr", dtype=xp.float32)
    if adj.nnz:
        H = H - xp.float32(r_value) * adj

    if k is None:
        # If k is omitted, estimate k as the number of negative eigenvalues
        # among the smallest computed algebraic eigenpairs (<= max_k).
        n_eigs = min(max_k, n_nodes - 1)
    else:
        # If k is provided, use the k smallest algebraic eigenvalues.
        n_eigs = k

    # Compute informative (negative) Bethe-Hessian eigenvalues from smallest algebraic eigenpairs.
    eigenvalues, U = eigsh(H, k=n_eigs, which="SA")

    if k is None:
        # Count negative eigenvalues to estimate k, with a tolerance for numerical noise.
        k_eff = int(xp.sum(xp.asarray(eigenvalues) < -negative_tol))
        if k_eff > max_k:
            # Even if the estimated number of communities exceeds max_k, truncate to max_k.
            warn(f"Estimated number of communities ({k_eff}) exceeds `max_k` ({max_k}).")
            k_eff = max_k
    else:
        # Use the provided k directly.
        k_eff = k

    if k_eff <= 1:
        # No informative (negative) directions: return trivial one-community partition.
        return [0 for _ in range(n_nodes)]
    if k_eff < n_eigs:
        # Truncate to the effective number of communities.
        U = U[:, :k_eff]

    # Row-normalize embeddings (Ng et al., 2002).
    norms = xp.linalg.norm(U, axis=1, keepdims=True)
    norms = xp.where(norms < xp.float32(1e-10), xp.float32(1.0), norms)
    U = U / norms

    km = KMeans(n_clusters=k_eff, random_state=seed, n_init=n_init, max_iter=max_iter)
    labels_gpu = km.fit_predict(U.astype(xp.float32, copy=False))
    labels = xp.asarray(labels_gpu).astype(int, copy=False)
    return labels.tolist()
