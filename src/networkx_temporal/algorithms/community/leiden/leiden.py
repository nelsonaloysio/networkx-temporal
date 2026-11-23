import logging as log
from inspect import signature
from typing import List, Optional, Union
from warnings import warn

import numpy as np

from ....classes import is_static_graph, is_temporal_graph
from ....typing import TemporalGraph, StaticGraph

from .temporal import leiden_communities_temporal
from ...gpu import NX_GPU_AUTOCONFIG, NX_CUGRAPH_AUTOCONFIG
from ....classes import is_temporal_graph
from ....typing import TemporalGraph, StaticGraph, Literal

BACKEND = Literal["networkx_temporal", "leidenalg", "cugraph"]
BACKENDS = list(BACKEND.__args__)


def leiden_communities(
    graph: Union[TemporalGraph, StaticGraph],
    device: Optional[Literal["cpu", "gpu"]] = None,
    backend: Optional[BACKEND] = None,
    **kwargs
) -> Union[dict, List[dict]]:
    """ Leiden algorithm for community detection.
    Optimizes
    :func:`~networkx_temporal.algorithms.modularity_multislice` if ``graph`` is a
    :class:`~networkx_temporal.classes.TemporalGraph` object, or
    :func:`~networkx_temporal.algorithms.modularity` if ``graph`` is a static NetworkX graph
    object.

    High-level function that dispatches to CPU or GPU
    devices based on ``backend`` and ``device``.
    The ``backend`` parameter controls which algorithm implementation is used.
    Available choices are:

    - ``'networkx_temporal'``: Default backend (CPU/GPU). Calls
      :func:`~networkx_temporal.algorithms.leiden_communities_temporal`.

    - ``'leidenalg'``: Sequential optimization with `leidenalg <https://leidenalg.readthedocs.io>`__
      for static/temporal graphs (CPU only).

    - ``'cugraph'``: Parallelized optimization with `cuGraph <https://docs.rapids.ai/api/cugraph/stable/>`__
      for static graphs (NVIDIA GPUs only).

    Results may differ between backends and runs due to parallelism and floating point precision.
    Note that backends accept different keyword arguments; see their documentation for details.

    .. seealso::

        - The `Examples → GPU acceleration → Leiden communities
          <../examples/gpu.html#leiden-communities>`__ page for usage examples.
        - The `Examples → GPU acceleration → Compare running times
          <../examples/gpu.html#compare-running-times>`__
          and `Examples → GPU acceleration → Compare detection accuracy
          <../examples/gpu.html#compare-detection-accuracy>`__
          sections for efficiency/efficacy comparisons.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX
        graph object.
    :param str device: Device to use for computation. Optional. Available choices:

        - ``'cpu'``: Available for the default backend or ``'leidenalg'``.

        - ``'gpu'``: Available for the default backend or ``'cugraph'``.
          Used by default if ``NX_GPU_AUTOCONFIG=1`` is set on the environment on import.

    :param str backend: Backend to use for computation. Optional.

        - ``'networkx_temporal'`` (default): Calls
          :func:`~networkx_temporal.algorithms.leiden_communities_temporal`.

        - ``'leidenalg'``: Calls
          `leidenalg find_partition <https://leidenalg.readthedocs.io/en/stable/reference.html#leidenalg.find_partition>`__
          or `find_partition_temporal <https://leidenalg.readthedocs.io/en/stable/reference.html#leidenalg.find_partition_temporal>`__.

        - ``'cugraph'``: Calls
          `cuGraph Leiden <https://docs.nvidia.com/cugraph/latest/api_docs/api/cugraph/cugraph.leiden/>`__.
          Not available for temporal graphs.

    :param kwargs: Keyword arguments to pass to the backend caller.
    """
    device, backend = _resolve_pathway(device, backend)

    if device not in ("cpu", "gpu"):
        raise ValueError(f"Unsupported device: '{device}', expects 'cpu' or 'gpu'.")

    if backend == "networkx_temporal":
        fnc = leiden_communities_temporal
        kwargs["device"] = device
    elif backend == "leidenalg":
        if device != "cpu":
            raise ValueError(f"Unsupported device for '{backend}' backend: '{device}'.")
        fnc = _leiden_communities_leidenalg
    elif backend == "cugraph":
        if device != "gpu":
            raise ValueError(f"Unsupported device for '{backend}' backend: '{device}'.")
        if is_temporal_graph(graph):
            raise ValueError(f"Unsupported backend for temporal graphs: '{backend}'.")
        fnc = _leiden_communities_cugraph
    else:
        raise ValueError(f"Invalid backend: '{backend}' not in {BACKENDS}.")

    assignments = fnc(graph, **kwargs)
    return assignments


def _leiden_communities_leidenalg(graph: Union[TemporalGraph, StaticGraph], **kwargs):
    """ CPU-based Leiden optimization via leidenalg/igraph.
    """
    from ....utils.convert.igraph import to_igraph

    try:
        import leidenalg as la
    except ImportError as e:
        raise ImportError(
            "The `leidenalg` package is required to use this backend. "
            "Available from PyPI: `pip install leidenalg`."
        ) from e

    iG = graph  # Assume the input graph is already an igraph object.
    if is_static_graph(graph):
        iG = to_igraph(graph)
        vertex_id_attr = "_nx_name"
    elif is_temporal_graph(graph):
        iG = [to_igraph(g) for g in graph]
        vertex_id_attr = "_nx_name"

    # Select function based on whether input is a single graph or a sequence of graphs.
    fnc = la.find_partition_temporal if type(iG) == list else la.find_partition
    # Optimizer function; defaults to ModularityVertexPartition if unset.
    opt = kwargs.pop("partition_type", la.ModularityVertexPartition)

    defaults = {
        "vertex_id_attr": vertex_id_attr,  #   str
        "n_iterations": 2,                 #   int
        "max_comm_size": 0,                #   int
        "interslice_weight": 1.0,          #   float
        "slice_attr": "slice",             #   str
        "edge_type_attr": "type",          #   str
        "weight_attr": "weight",           #   str
        "initial_membership": None,        #   Optional[List[int]]
        "weights": None,                   #   Optional[str]
        "seed": None,                      #   Optional[int]
    }
    # Inspect the function signature to filter out unsupported keyword arguments.
    fnc_sig = signature(fnc)
    fnc_kwargs = {k: v for k, v in {**defaults, **kwargs}.items() if k in fnc_sig.parameters and v}

    # Inspect the optimizer signature to filter out unsupported keyword arguments.
    # NOTE: Some optimizer functions take the same argument names as the main function.
    opt_sig = signature(opt)
    opt_kwargs = {k: v for k, v in {**defaults, **kwargs}.items() if k in opt_sig.parameters and v}

    # Validate that all arguments are valid for the selected algorithm and optimizer.
    valid_kwargs = set(fnc_sig.parameters) | set(opt_sig.parameters)
    if any(k not in valid_kwargs and v is not None for k, v in kwargs.items()):
        invalid_kwargs = set(kwargs) - set(fnc_sig.parameters) - set(opt_sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for {fnc.__name__} with {opt.__name__}. "
            f"\nSupported {fnc.__name__} arguments: {set(fnc_sig.parameters)}. "
            f"\nSupported {opt.__name__} arguments: {set(opt_sig.parameters)}."
        )

    # Run the Leiden algorithm with the selected optimizer and filtered kwargs.
    partition = fnc(iG, opt, **{**fnc_kwargs, **opt_kwargs})

    if fnc == la.find_partition:
        membership = partition.membership
        log.debug("leidenalg modularity: %s", partition.quality)
    else:
        membership, modularity = partition
        log.debug("leidenalg modularity: %s", modularity)

    return membership


def _leiden_communities_cugraph(graph: StaticGraph, **kwargs):
    """ GPU-based Leiden optimization of static modularity via nx-cugraph/pylibcugraph.
    """
    from ....utils.convert.cugraph import to_cugraph

    try:
        import cupy as cp
        import pylibcugraph as plc
    except ImportError as exc:
        raise ImportError(
            "The cupy, nx-cugraph, and pylibcugraph. "
            "Available with  "
            "`conda install -c rapidsai -c nvidia -c conda-forge "
            "cugraph nx-cugraph pylibcugraph`."
        ) from exc

    weight = kwargs.get("weight", "weight")

    cuG = graph  # Assume the input graph is already a cuGraph object.
    if is_static_graph(graph):  # Or convert if static NetworkX graph.
        cuG = to_cugraph(graph, weight=weight, use_compat_graph=False)

    n_nodes = cuG.number_of_nodes()
    cuG = cuG._get_plc_graph(weight, 1, np.float32)

    # Inspect algorithm signature, filter kwargs and raise an error for unsupported arguments.
    # NOTE: cuGraph Leiden requires all six arguments below to be passed on function call.
    defaults = {
        "weight": weight,             # str
        "resolution": 1.0,            # float
        "theta": 1.0,                 # float
        "max_level": 500,             # float
        "random_state": None,         # Optional[float]
        "do_expensive_check": False,  # bool
    }
    fnc_sig = signature(plc.leiden)
    fnc_kwargs = {k: v for k, v in {**defaults, **kwargs}.items() if k in fnc_sig.parameters}

    if any(k not in fnc_sig.parameters for k in kwargs):
        invalid_kwargs = set(kwargs) - set(fnc_sig.parameters)
        raise ValueError(
            f"Invalid arguments {invalid_kwargs} for {plc.leiden.__name__}. "
            f"Supported keywords are: {set(fnc_sig.parameters)}."
        )

    node_ids, clusters, _modularity = plc.leiden(
        graph=cuG,
        resource_handle=plc.ResourceHandle(),
        **fnc_kwargs,
    )
    log.debug("CuGraph Leiden modularity: %s", _modularity)

    # Vertices missing from the result (isolates) become their own singletons.
    membership = np.full(n_nodes, -1, dtype=np.int64)
    membership[cp.asnumpy(node_ids)] = cp.asnumpy(clusters)
    isolated = membership < 0
    if isolated.any():
        membership[isolated] = membership.max() + 1 + np.arange(int(isolated.sum()))
    return np.unique(membership, return_inverse=True)[1].astype(int).tolist()


def _leiden_multislice_gpu(graph: Union[TemporalGraph, StaticGraph], **kwargs):
    """ Parallelized multislice Leiden algorithm on GPU.

    :meta private:
    """
    warn(
        "The `leiden_multislice_gpu` function is deprecated in favor of  `leiden_communities"
        "(..., backend='cupy', device='gpu')` and will be removed in a future release.",
        DeprecationWarning
    )
    return leiden_communities_temporal(graph, **{**kwargs, "device": "gpu"})


def _resolve_pathway(device, backend):
    """ Resolves device and backend into ``str, str`` tuple.
    """
    cpu_only = ("leidenalg",)
    gpu_only = ("cugraph",)

    if backend is None:
        if NX_CUGRAPH_AUTOCONFIG:
            backend = "cugraph"
        else:
            backend = "networkx_temporal"

    if device is None:
        if backend in gpu_only:
            device = "gpu"
        elif NX_GPU_AUTOCONFIG and backend not in cpu_only:
            device = "gpu"
        else:
            device = "cpu"

    return device, backend
