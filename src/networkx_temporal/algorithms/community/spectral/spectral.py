from inspect import signature
from typing import List, Optional, Union

from .bethe_hessian import spectral_clustering_bethe_hessian
from .laplacian import spectral_clustering_laplacian
from .modularity import spectral_clustering_modularity
from ...cugraph import NX_CUGRAPH_AUTOCONFIG
from ....classes.types import is_temporal_graph
from ....typing import Literal, StaticGraph, TemporalGraph
from ....utils import to_supra_adjacency_matrix

OPERATOR = Literal["laplacian", "bethe_hessian", "modularity"]
OPERATORS = list(OPERATOR.__args__)

DEVICE = "gpu" if NX_CUGRAPH_AUTOCONFIG else "cpu"


def spectral_clustering(
    graph: Union[TemporalGraph, StaticGraph],
    operator: OPERATOR = "laplacian",
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    device: Literal["cpu", "gpu"] = DEVICE,
    **kwargs,
) -> Union[dict, List[dict]]:
    """ Spectral clustering of a temporal or static graph.

    Computes the spectral partition of a temporal or static graph by constructing the
    supra-adjacency matrix and applying :math:`k`-means on the eigenvectors of the specified
    ``operator``:

    - ``'laplacian'``: normalized or unnormalized operator with
      :func:`~networkx_temporal.algorithms.community.spectral.spectral_clustering_laplacian`;

    - ``'bethe_hessian'``: Bethe-Hessian operator with
      :func:`~networkx_temporal.algorithms.community.spectral.spectral_clustering_bethe_hessian`;

    - ``'modularity'``: modularity-based spectral clustering with
      :func:`~networkx_temporal.algorithms.community.spectral.spectral_clustering_modularity`.

    .. seealso::

        The `Examples → GPU acceleration → Spectral clustering
        <../examples/gpu.html#spectral-clustering>`__ page for examples.

    .. hint::

       Setting ``NX_CUGRAPH_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param operator: The spectral operator to use. Supported types are
        ``'laplacian'``, ``'bethe_hessian'``, and ``'modularity'``. Default is ``'laplacian'``.
    :param weight: Edge attribute to use as weight. If unset, treat edges as unweighted.
    :param interslice_weight: Weight of inter-slice edges connecting node copies across snapshots.
    :param device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses NumPy, SciPy, and scikit-learn (default).

        - ``'gpu'``: Uses CuPy, CuPy sparse, and RAPIDS cuML (NVIDIA).

    .. rubric:: Example

    Computing the spectral partition of an example SBM graph:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>>
        >>> y = tx.algorithms.community.spectral.spectral_clustering(
        >>>     TG, device='cpu', operator="modularity")

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.

    :note: GPU acceleration requires the CuPy and RAPIDS cuML libraries.
    """
    if device not in ("cpu", "gpu"):
        raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")
    if graph.is_directed():
        raise ValueError("GPU spectral clustering requires an undirected graph.")

    if operator == "laplacian":
        fnc = spectral_clustering_laplacian
    elif operator == "bethe_hessian":
        fnc = spectral_clustering_bethe_hessian
    elif operator == "modularity":
        fnc = spectral_clustering_modularity
    else:
        raise ValueError(f"Invalid operator: '{operator}' not in {OPERATORS}.")

    adj, offsets = to_supra_adjacency_matrix(
        graph,
        weight=weight,
        interslice_weight=interslice_weight,
        device=device,
        return_offsets=True,
    )

    # Inspect function signature, filter kwargs and raise an error for unsupported arguments.
    sig = signature(fnc)
    fnc_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

    fnc_kwargs["device"] = device
    if operator == "modularity":
        fnc_kwargs["offsets"] = offsets

    if any(k not in sig.parameters for k in kwargs):
        invalid_kwargs = set(kwargs) - set(sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for '{fnc.__name__}'. "
            f"Supported keywords are: {set(sig.parameters)}."
        )

    # Compute the spectral partition using the specified device and operator.
    assignments = fnc(adj, **fnc_kwargs)

    if is_temporal_graph(graph):
        return [
            assignments[offsets[t]:offsets[t] + len(graph[t])]
            for t in range(len(graph))
        ]

    return assignments
