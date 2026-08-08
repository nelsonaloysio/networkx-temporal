from inspect import signature
from typing import List, Optional, Union

import numpy as np

from .multislice_gpu import leiden_multislice_gpu
from ...gpu import NX_GPU_AUTOCONFIG, NX_CUGRAPH_AUTOCONFIG
from ....classes.functions import is_static_graph, is_temporal_graph
from ....typing import TemporalGraph, StaticGraph, Literal
from ....utils.convert.cugraph import to_cugraph
from ....utils.convert.igraph import to_igraph


def leiden_communities(
    graph: Union[TemporalGraph, StaticGraph],
    gamma: Optional[float] = None,
    weight: Optional[str] = None,
    interslice_weight: Optional[float] = 1.0,
    max_iter: Optional[int] = None,
    seed: Optional[int] = None,
    device: Optional[Literal["cpu", "gpu"]] = None,
    **kwargs,
) -> Union[dict, List[dict]]:
    """ Returns the Leiden partition of a graph.

    If ``graph`` is a :class:`~networkx_temporal.classes.TemporalGraph`, optimize (temporal)
    :func:`~networkx_temporal.algorithms.modularity_multislice` on
    the temporal graph using the specified device. If ``graph`` is a static graph, optimize
    (static) :func:`~networkx_temporal.algorithms.modularity`.

    The GPU-based Leiden optimization of multislice modularity is parallelized and uses sparse
    `CuPy <https://cupy.dev/>`__ as a backend on single devices (AMD/NVIDIA). The
    `leidenalg <https://leidenalg.readthedocs.io/en/stable/api.html#leidenalg.find_partition>`__
    backend is used on CPU instead, and is preferrable For accuracy-sensitive tasks at the cost of
    longer runtimes.

    .. hint::

       Setting ``NX_GPU_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    .. seealso::

       The `Examples → GPU acceleration → Leiden communities
       <../examples/gpu.html#leiden-communities>`__ page for examples.

    :param graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param gamma: Resolution parameter :math:`\\gamma` (default: ``1.0``).
        Controls the size of communities; higher values lead to smaller communities.
        Only used when ``device='gpu'``; ignored when ``device='cpu'``.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
        Only used when ``graph`` is a :class:`~networkx_temporal.classes.TemporalGraph`.
    :param max_iter: Maximum coarsening levels. Default: ``2`` for CPU and ``500`` for GPU.
        If ``-1``, run until convergence (CPU only).
    :param seed: Random seed number for reproducibility.
    :param str device: Device to use for computation. Available choices:

        - ``'cpu'``: Uses `igraph <https://igraph.org/python/>`__ and
          `leidenalg <https://leidenalg.readthedocs.io>`__ as backends.

        - ``'gpu'``: Uses `cuGraph <https://docs.rapids.ai/api/cugraph/stable/>`__ and
          `CuPy <https://cupy.dev/>`__ as backends.

    :param kwargs: Additional keyword arguments to pass to the backend.

        - ``device='cpu'``: leidenalg's
          `find_partition <https://leidenalg.readthedocs.io/en/stable/api.html#leidenalg.find_partition>`__
          and `find_partition_temporal
          <https://leidenalg.readthedocs.io/en/stable/api.html#leidenalg.find_partition_temporal>`__.

        - ``device='gpu'``: cuGraph's
          `leiden <https://docs.rapids.ai/api/libcugraph/stable/api.html#leiden>`__
          (NVIDIA) for static graphs and
          :func:`~networkx_temporal.algorithms.leiden_multislice_gpu`
          using CuPy (AMD/NVIDIA) for temporal graphs.
          A backend may be enforced by passing the appropriate graph.
    """
    device = _resolve_device(device, graph)
    gamma = 1.0 if gamma is None else gamma

    if device == "cpu":
        fnc = _leiden_cpu
        if is_temporal_graph(graph):
            # Multislice modularity optimization with igraph/leidenalg backend.
            kwargs.update({
                "weights": weight,
                "n_iterations": max_iter,
                "seed": seed,
                "weight_attr": weight,
                "interslice_weight": interslice_weight,
                "vertex_id_attr": "_nx_name",
                # "resolution_parameter": gamma,
                # "edge_type_attr": "interslice",
                # "slice_attr": "slice",
            })
        else:  # Static modularity optimization with igraph/leidenalg backend.
            kwargs.update({
                "weights": weight,
                "n_iterations": max_iter,
                "seed": seed,
                # "resolution_parameter": gamma,
            })

    elif device == "gpu":
        if is_temporal_graph(graph):
            # Parallelized multislice modularity optimization with cupy backend.
            fnc = leiden_multislice_gpu
            kwargs.update({
                "gamma": gamma,
                "weight": weight,
                "interslice_weight": interslice_weight,
                "refine": kwargs.get("refine", True),
                "max_iter": max_iter or 500,
                "max_sweeps": kwargs.get("max_sweeps", 100),
                "seed": seed,
            })
        else:  # Static modularity optimization with pylibcugraph/nx-cugraph backend.
            fnc = _leiden_static_gpu
            kwargs.update({
                "resolution": gamma,
                "weight": weight,
                "theta": kwargs.get("theta", 1.0),
                "max_level": max_iter or 500,
                "random_state": seed,
                "do_expensive_check": kwargs.get("do_expensive_check", False),
            })

    else:
        raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")

    return fnc(graph, **kwargs)


def _leiden_cpu(
    graph: Union[TemporalGraph, StaticGraph],
    # partition_type: Optional[object] = la.ModularityVertexPartition,
    # initial_membership: Optional[List[int]] = None,
    # weights: Optional[str] = None,
    # n_iterations: int = 2,
    # max_comm_size: int = 0,
    # seed: Optional[int] = None,
    # interslice_weight: float = 1,
    # slice_attr: str = 'slice',
    # vertex_id_attr: str = 'id',
    # edge_type_attr: str = 'type',
    # weight_attr: str = 'weight',
    **kwargs,
) -> Union[List[int], List[List[int]]]:
    """ CPU-based Leiden optimization via leidenalg/igraph.
    """
    try:
        import leidenalg as la
    except ImportError as e:
        raise ImportError(
            "The `leidenalg` package is required to use the Leiden algorithm. "
            "Please install it via `pip install leidenalg`."
        ) from e

    if is_static_graph(graph):
        iG = to_igraph(graph)
        fnc = la.find_partition
    else:
        iG = [to_igraph(g) for g in graph]
        fnc = la.find_partition_temporal

    # Optimizer function; defaults to ModularityVertexPartition if unset.
    opt = kwargs.pop("partition_type", la.ModularityVertexPartition)

    # Inspect the function signature to filter out unsupported keyword arguments.
    fnc_sig = signature(fnc)
    fnc_kwargs = {k: v for k, v in kwargs.items() if k in fnc_sig.parameters and v is not None}

    # Inspect the optimizer signature to filter out unsupported keyword arguments.
    # NOTE: Some optimizer functions take the same argument names as the main function.
    opt_sig = signature(opt)
    opt_kwargs = {k: v for k, v in kwargs.items() if k in opt_sig.parameters and v is not None}

    # Validate that all arguments are valid for the selected algorithm and optimizer.
    valid_kwargs = set(fnc_sig.parameters) | set(opt_sig.parameters)
    if any(k not in valid_kwargs and v is not None for k, v in kwargs.items()):
        invalid_kwargs = set(kwargs) - set(fnc_sig.parameters) - set(opt_sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for '{fnc.__name__}' with '{opt.__name__}'. "
            f"\nSupported {fnc.__name__} arguments: {set(fnc_sig.parameters)}. "
            f"\nSupported {opt.__name__} arguments: {set(opt_sig.parameters)}."
        )

    # Run the Leiden algorithm with the selected optimizer and filtered kwargs.
    partition = fnc(iG, opt, **{**fnc_kwargs, **opt_kwargs})

    if is_static_graph(graph):
        membership = partition.membership
    else:
        membership, _ = partition

    return membership


def _leiden_static_gpu(
    graph: StaticGraph,
    weight: Optional[str] = "weight",
    resolution: float = 1.0,
    theta: float = 1.0,
    max_level: float = 500,
    random_state: Optional[float] = None,
    do_expensive_check: float = False,
    **kwargs,
) -> List[int]:
    """ GPU-based Leiden optimization of static modularity via nx-cugraph/pylibcugraph.
    """
    try:
        import cupy as cp
        import pylibcugraph as plc
    except ImportError as exc:
        raise ImportError(
            "GPU Leiden requires cupy, nx-cugraph, and pylibcugraph. "
            "Please install it via "
            "`conda install -c rapidsai -c nvidia -c conda-forge "
            "cugraph nx-cugraph pylibcugraph`."
        ) from exc

    cuG = graph  # Assume the input graph is already a cuGraph object.
    if is_static_graph(graph):  # Or convert if static NetworkX graph.
        cuG = to_cugraph(graph, weight=weight, use_compat_graph=False)

    n_nodes = cuG.number_of_nodes()
    cuG = cuG._get_plc_graph(weight, 1, np.float32)

    # Inspect algorithm signature, filter kwargs and raise an error for unsupported arguments.
    fnc_sig = signature(plc.leiden)
    fnc_kwargs = {
        "resolution": resolution,
        "theta": theta,
        "max_level": max_level,
        "random_state": random_state,
        "do_expensive_check": do_expensive_check,
    }
    fnc_kwargs.update({k: v for k, v in kwargs.items() if k in fnc_sig.parameters})

    if any(k not in fnc_sig.parameters for k in kwargs):
        invalid_kwargs = set(kwargs) - set(fnc_sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for '{plc.leiden.__name__}'. "
            f"Supported keywords are: {set(fnc_sig.parameters)}."
        )

    node_ids, clusters, _modularity = plc.leiden(
        graph=cuG,
        resource_handle=plc.ResourceHandle(),
        **fnc_kwargs,
    )

    # Vertices missing from the result (isolates) become their own singletons.
    membership = np.full(n_nodes, -1, dtype=np.int64)
    membership[cp.asnumpy(node_ids)] = cp.asnumpy(clusters)
    isolated = membership < 0
    if isolated.any():
        membership[isolated] = membership.max() + 1 + np.arange(int(isolated.sum()))
    return np.unique(membership, return_inverse=True)[1].astype(int).tolist()


def _resolve_device(device, graph):
    """ Explicit arg > NX_GPU_AUTOCONFIG > NX_CUGRAPH_AUTOCONFIG.

    NX_CUGRAPH_AUTOCONFIG only promotes the static (cuGraph) path — never
    multislice, which runs on CuPy and is not a cuGraph backend.
    """
    if device is not None:
        return device
    if NX_GPU_AUTOCONFIG:
        return "gpu"
    if NX_CUGRAPH_AUTOCONFIG and not is_temporal_graph(graph):
        return "gpu"
    return "cpu"
