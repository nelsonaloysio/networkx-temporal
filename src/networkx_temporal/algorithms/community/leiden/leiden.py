import logging as log
from inspect import signature
from typing import List, Optional, Union

import numpy as np

from .parallel import leiden_communities_parallel
from ...gpu import NX_GPU_AUTOCONFIG, NX_CUGRAPH_AUTOCONFIG
from ....classes import is_static_graph, is_temporal_graph
from ....typing import TemporalGraph, StaticGraph, Literal
from ....utils.convert.cugraph import to_cugraph
from ....utils.convert.igraph import to_igraph


def leiden_communities(
    graph: Union[TemporalGraph, StaticGraph],
    weight: Optional[str] = None,
    interslice_weight: Optional[float] = 1.0,
    gamma: Optional[float] = None,
    theta: Optional[float] = None,
    refine: Optional[bool] = None,
    max_iter: Optional[int] = None,
    max_sweeps: Optional[int] = None,
    seed: Optional[int] = None,
    device: Optional[Literal["cpu", "gpu"]] = None,
    backend: Optional[Literal["leidenalg", "cugraph"]] = None,
    **kwargs
) -> Union[dict, List[dict]]:
    """ Returns the Leiden partition of a graph. High-level function that dispatches to CPU or GPU
    devices based on the ``device`` and ``backend`` parameters.
    Optimizes
    :func:`~networkx_temporal.algorithms.modularity_multislice` if ``graph`` is a
    :class:`~networkx_temporal.classes.TemporalGraph` object, or
    :func:`~networkx_temporal.algorithms.modularity` if ``graph`` is a static NetworkX graph
    object.

    The ``backend`` parameter controls which algorithm implementation is used. If ``None``
    (default), calls :func:`~networkx_temporal.algorithms.leiden_communities_parallel` for either
    CPU or GPU devices. Other available choices:

    - ``'leidenalg'``: Sequential optimization with `leidenalg <https://leidenalg.readthedocs.io>`__
      for static/temporal graphs (CPU only).

    - ``'cugraph'``: Parallelized optimization with `cuGraph <https://docs.rapids.ai/api/cugraph/stable/>`__
      for static graphs (NVIDIA GPUs only).

    Results may differ between backends and runs due to parallelism and floating point precision.
    Note that not all parameters are supported by all backends; see their documentation for
    details.

    .. hint::

        Setting ``NX_GPU_AUTOCONFIG=1`` in the environment will set ``device='gpu'`` as default.

    .. seealso::

        The `Examples → GPU acceleration → Leiden communities
        <../examples/gpu.html#leiden-communities>`__ page for usage examples.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Inter-slice coupling strength for temporal graphs. Default: ``1.0``.
        Only used when ``graph`` is a :class:`~networkx_temporal.classes.TemporalGraph`.
    :param gamma: Resolution parameter :math:`\\gamma` (default: ``1.0``).
        Controls the size of communities; higher values lead to smaller communities.
        Ignored if ``backend='leidenalg'``.
    :param theta: Parallelized sweep control parameter :math:`\\theta` (default: ``1.0``).
        Used if ``backend='cugraph'``.
    :param max_iter: Maximum coarsening levels. Default: ``500``.
    :param max_sweeps: Maximum sweeps per phase, per iteration. Default: ``500``.
        Used for parallelized local moving and refinement phases (``backend='cupy' or 'cugraph'``).
    :param refine: Whether to run the refinement phase of Leiden. Default is ``True``.
        If ``False``, yields a slightly faster Louvain-like algorithm.
    :param seed: Random seed number for reproducibility. Note that parallelized GPU computations
        may not be fully deterministic across runs.
    :param str device: Device to use for computation. Optional. Available choices:

            - ``'cpu'``: Available for the default backend or ``'leidenalg'``.

            - ``'gpu'``: Available for the default backend or ``'cugraph'`` (NVIDIA only).

    :param str backend: Alternative backend to use for computation. Optional.
        If unset (``None``), calls
        :func:`~networkx_temporal.algorithms.leiden_communities_parallel` by default.
        Available choices:

        - ``'leidenalg'``: Calls
          `leidenalg find_partition <https://leidenalg.readthedocs.io/en/stable/reference.html#leidenalg.find_partition>`__
          or `find_partition_temporal <https://leidenalg.readthedocs.io/en/stable/reference.html#leidenalg.find_partition_temporal>`__.

        - ``'cugraph'``: Calls
          `cuGraph Leiden <https://docs.nvidia.com/cugraph/latest/api_docs/api/cugraph/cugraph.leiden/>`__.
          Not available for temporal graphs.
    """
    device = _resolve_device(device, graph, backend)

    if backend is None:
        return leiden_communities_parallel(
            graph,
            weight=weight,
            interslice_weight=interslice_weight or 1.0,
            gamma=gamma or 1.0,
            refine=refine or True,
            max_iter=max_iter or 500,
            max_sweeps=max_sweeps or 100,
            seed=seed,
            device=device,
            **kwargs
        )

    if backend == "leidenalg":
        if device != "cpu":
            raise ValueError(f"Unsupported device: '{device}' (backend='leidenalg' requires CPU).")
        if is_temporal_graph(graph) or type(graph) == list:
            return _leiden_communities_leidenalg(
                graph,
                weights=weight,
                weight_attr=weight,
                interslice_weight=interslice_weight or 1.0,
                n_iterations=max_iter or 2,
                seed=seed,
                vertex_id_attr="_nx_name",
            )
        return _leiden_communities_leidenalg(
            graph,
            weights=weight,
            n_iterations=max_iter or 2,
            seed=seed,
        )

    if backend == "cugraph":
        if device != "gpu":
            raise ValueError(f"Unsupported device: '{device}' (backend='cugraph' requires GPU).")
        return _leiden_communities_cugraph(
            graph,
            weight=weight,
            resolution=gamma or 1.0,
            theta=theta or 1.0,
            max_level=max_iter or 500,
            random_state=seed,
            do_expensive_check=kwargs.get("do_expensive_check", False),
        )

    raise ValueError(
        f"Unsupported backend: '{backend}', expects 'leidenalg', or 'cugraph' if set.")


def _leiden_communities_leidenalg(
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
    **kwargs
):
    """ CPU-based Leiden optimization via leidenalg/igraph.
    """
    try:
        import leidenalg as la
    except ImportError as e:
        raise ImportError(
            "The `leidenalg` package is required to use the Leiden algorithm. "
            "Please install it via `pip install leidenalg`."
        ) from e

    iG = graph  # Assume the input graph is already an igraph object.
    if is_static_graph(graph):
        iG = to_igraph(graph)
    elif is_temporal_graph(graph):
        iG = [to_igraph(g) for g in graph]

    # Select function based on whether input is a single graph or a sequence of graphs.
    fnc = la.find_partition_temporal if type(iG) == list else la.find_partition

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


def _leiden_communities_cugraph(
    graph: StaticGraph,
    # weight: Optional[str] = "weight",
    # resolution: float = 1.0,
    # theta: float = 1.0,
    # max_level: float = 500,
    # random_state: Optional[float] = None,
    # do_expensive_check: float = False,
    **kwargs,
):
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

    weight = kwargs.get("weight", "weight")

    cuG = graph  # Assume the input graph is already a cuGraph object.
    if is_static_graph(graph):  # Or convert if static NetworkX graph.
        cuG = to_cugraph(graph, weight=weight, use_compat_graph=False)

    n_nodes = cuG.number_of_nodes()
    cuG = cuG._get_plc_graph(weight, 1, np.float32)

    # Inspect algorithm signature, filter kwargs and raise an error for unsupported arguments.
    fnc_sig = signature(plc.leiden)
    fnc_kwargs = {k: v for k, v in kwargs.items() if k in fnc_sig.parameters}

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


def _resolve_device(device, graph, backend):
    """ Resolves to CPU or GPU device based on parameters and environment variables.
    """
    if device is not None:
        return device
    if NX_GPU_AUTOCONFIG:
        return "gpu"
    if NX_CUGRAPH_AUTOCONFIG and not is_temporal_graph(graph):
        return "gpu"
    if backend == "leidenalg":
        return "cpu"
    if backend == "cugraph":
        return "gpu"
    return "cpu"
