from typing import List, Optional, Union

import networkx as nx

from .modularity_spectral import modularity_spectral
from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph
from ...utils import map_attr_to_nodes, partition_nodes
from ...utils.convert import to_numpy, to_scipy


def modularity(
    graph: Union[TemporalGraph, StaticGraph],
    communities: Union[str, list, dict],
    weight: Optional[str] = "weight",
    resolution: Optional[float] = 1,
    spectral: bool = False,
    sparse: bool = False,
) -> Union[float, List[float]]:
    """ Returns the modularity of a graph.

    Modularity [7]_ measures the fraction of edges in a graph that fall within communities,
    compared to their expected number in a random graph with the same degree sequence.
    Higher values may indicate more internal connections than expected by chance.
    It is commonly defined as:

    .. math::

        Q =
        \\frac{1}{2m} \\sum_{(i,j) \\in V^2}
        \\left[ A_{ij} - \\gamma \\frac{d_i^{out} \\, d_j^{in}}{2m} \\right]
        \\delta(c_i, c_j),

    where
    :math:`m` is the number of edges in the graph,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`d` are node in/out-degrees,
    :math:`c` are their communities,
    and :math:`\\gamma = 1` (default) is the resolution parameter [4]_,
    where smaller values favor larger communities, including negative values.

    This can be reduced to a summation over communities, which is more efficient to compute:

    .. math::

        Q = \\sum_{c \\in C} \\left[ \\frac{L_c}{m} - \\gamma
        \\left( \\frac{d_c}{2m} \\right)^2 \\right],

    where :math:`L_c` is the number of within-community edges
    and :math:`d_c` is the sum of degrees of nodes in community :math:`c`.
    If ``spectral=True``, modularity is computed using
    :func:`~networkx_temporal.algorithms.modularity_spectral` instead.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.multislice_modularity` function for a temporal
        generalization of the metric.

    .. [7] A. Clauset, M. E. J. Newman, C. Moore (2004). ''Finding community structure in very
        large networks.'' Phys. Rev. E 70.6 (2004).
        doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param communities: String (node attribute key), list of community assignments,
        or dict mapping node to community.
    :param resolution: The resolution parameter. Defaults to ``1``.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param spectral: Whether to use the spectral method to compute modularity.
        If ``False``, use `NetworkX modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__
        (default).
    :param sparse: Whether to use a sparse matrix representation for the spectral method.
        Only applicable if ``spectral=True``. Default is ``False``.
    """
    resolution = 1 if resolution is None else resolution

    if not is_static_graph(graph) and not is_temporal_graph(graph):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if type(resolution) not in (int, float):
        raise TypeError("Resolution expects a numeric value.")
    if weight is not None and type(weight) != str:
        raise TypeError("Weight expects a string.")

    kwargs = {'weight': weight, 'resolution': resolution}
    to_matrix = to_scipy if sparse else to_numpy

    if spectral:
        fnc = modularity_spectral
        assignments = communities
        kwargs.update({"directed": graph.is_directed()})
        # Map to (n,) array or (n, k) matrix for spectral method.
        if type(communities) in (str, dict):
            assignments = map_attr_to_nodes(graph, communities, index=False)
        # Convert to sparse matrix if specified, otherwise dense array for spectral method.
        adj = to_matrix(graph, weight=weight)
    else:
        fnc = nx.algorithms.community.quality.modularity
        assignments = partition_nodes(graph, communities, index=False)

    if is_static_graph(graph):
        graph = adj if spectral else graph
        return Q(graph, assignments, **kwargs)

    graph = adj if spectral else graph
    return [fnc(g, z, **kwargs) for g, z in zip(graph, assignments)]
