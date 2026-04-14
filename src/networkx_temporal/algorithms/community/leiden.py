from typing import Callable, List, Optional, Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import TemporalGraph, StaticGraph
from ...utils.convert.igraph import to_igraph


def leiden_temporal_partition(
    TG: Union[TemporalGraph, StaticGraph],
    partition_type: Optional[Callable] = None,
    n_iterations: int = -1,
    interslice_weight: float = 1.0,
    seed: Optional[int] = None,
    **kwargs,
) -> Union[dict, List[dict]]:
    """ Returns the Leiden partition of a graph.

    The Leiden algorithm [10]_ is a community detection method that optimizes a
    quality function (e.g., modularity) to find the best partition of a graph into
    communities. For temporal graphs, a multislice modularity function is used to
    account for the temporal dimension of the graph.

    .. rubric:: Example

    Obtaining the temporal partition of a temporal graph with the Leiden algorithm
    and modularity as the quality function:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> ...

    Comparing ground truths with the Leiden partition of the example graph:

    .. code-block:: python

        ...

    .. [10] Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden:
        guaranteeing well-connected communities. Scientific reports, 9(1), 1-12.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param partition_type: The quality function to optimize. Can be a string (e.g., "modularity")
        or a callable function from the `leidenalg` library
        (e.g., ``leidenalg.ModularityVertexPartition``).
    :param n_iterations: The number of iterations to perform. Default is -1, which means to run
        until no further improvement can be made.
    :param interslice_weight: The weight of interslice edges for temporal graphs. Default is 1.0.
    :param seed: The random seed to use for the Leiden algorithm. Optional.
    :param kwargs: Additional keyword arguments to pass to the `leidenalg.find_partition` or
        ``leidenalg.find_temporal_partition`` function.

    :note: Requires ``igraph`` and ``leidenalg`` packages installed.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Input graph must be a TemporalGraph object.")

    try:
        import leidenalg as la
    except ImportError as e:
        raise ImportError(
            "The `leidenalg` package is required to use the Leiden algorithm. "
            "Please install it via `pip install leidenalg`."
        ) from e

    if partition_type is None:
        partition_type = la.ModularityVertexPartition

    if is_temporal_graph(TG):
        multislice_membership, _ = la.find_partition_temporal(
            to_igraph(TG),
            partition_type,
            n_iterations=n_iterations,
            interslice_weight=interslice_weight,
            vertex_id_attr="_nx_name",
            seed=seed,
            **kwargs
        )
        return multislice_membership

    return leiden_partition(TG, partition_type, n_iterations, interslice_weight, seed, **kwargs)


def leiden_partition(
    G: Union[TemporalGraph, StaticGraph],
    partition_type: Optional[Callable] = None,
    n_iterations: int = -1,
    seed: Optional[int] = None,
    **kwargs,
) -> Union[dict, List[dict]]:
    """ Returns the Leiden partition of a graph.

    The Leiden algorithm [10]_ is a community detection method that optimizes a
    quality function (e.g., modularity) to find the best partition of a graph into
    communities. This function considers each snapshot as a separate static graph
    and does not apply multislice optimization for time-aware community detection.

    If a temporal graph is given, the function returns a list of partitions, one for each snapshot.

    :param object G: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param partition_type: The quality function to optimize. Can be a string (e.g., "modularity")
        or a callable function from the `leidenalg` library
        (e.g., ``leidenalg.ModularityVertexPartition``).
    :param n_iterations: The number of iterations to perform. Default is -1, which means to run
        until no further improvement can be made.
    :param seed: The random seed to use for the Leiden algorithm. Optional.
    :param kwargs: Additional keyword arguments to pass to the `leidenalg.find_partition` or
        ``leidenalg.find_temporal_partition`` function.

    :note: Requires ``igraph`` and ``leidenalg`` packages installed.
    """
    if not is_static_graph(G) and not is_temporal_graph(G) and not type(G) == list:
        raise TypeError("Input graph must be a TemporalGraph or static NetworkX graph.")

    try:
        import leidenalg as la
    except ImportError as e:
        raise ImportError(
            "The `leidenalg` package is required to use the Leiden algorithm. "
            "Please install it via `pip install leidenalg`."
        ) from e

    if partition_type is None:
        partition_type = la.ModularityVertexPartition

    if is_temporal_graph(G) or type(G) == list:
        snapshot_membership = [
            la.find_partition(
                to_igraph(g),
                la.ModularityVertexPartition,
                n_iterations=n_iterations,
                seed=seed,
                **kwargs
            ).membership
            for g in G
        ]
        return snapshot_membership

    membership = la.find_partition(
        to_igraph(G),
        la.ModularityVertexPartition,
        n_iterations=n_iterations,
        seed=seed,
        **kwargs
    )
    return membership.membership
