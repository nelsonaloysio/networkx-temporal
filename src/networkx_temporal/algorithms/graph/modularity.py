from typing import Optional, Union

import networkx as nx

from ...typing import StaticGraph, TemporalGraph
from ...utils import is_temporal_graph, partitions


def modularity(
    G: Union[StaticGraph, TemporalGraph],
    partitions: Union[list, dict],
    weight: Optional[str] = "weight",
    resolution: float = 1,
) -> float:
    """
    Returns the modularity of a graph.

    Modularity [3]_ measures the fraction of edges in a graph that fall within communities,
    compared to their expected number if randomly placed in a network with the same order,
    size, and degree distribution (i.e., according to the configuration model). It is classically
    defined as:

    .. math::

        Q =
        \\frac{1}{2m} \\sum_{(i,j) \\in V^2}
        \\left[ \\mathbf{A}_{ij} - \\gamma \\frac{k_i k_j}{2m} \\right]
        \\delta(c_i, c_j),

    where
    :math:`m` is the number of (undirected) edges in the graph,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`k` and are node degrees,
    :math:`c` are their communities,
    and :math:`\\gamma = 1` (default) is the resolution parameter,
    where larger values favor smaller communities [4]_.
    It can be reduced to:

    .. math::

        Q = \\sum_{c \\in C} \\left[ \\frac{L_c}{m}
        - \\gamma \\left( \\frac{\\sum_{i \\in c} k_i}{2m} \\right)^2 \\right],

    where
    :math:`m` is the number of edges in the graph,
    :math:`L_c` is the number of edges within community :math:`c`,
    :math:`i \\in c` is a node in the community,
    :math:`k_i` is its degree,
    and :math:`\\gamma` is the resolution parameter.

    .. [3] Mark Newman (2018). ''Networks''. Oxford University Press, 2nd ed., pp. 498--514.

    .. [4] A. Clauset, M. E. J. Newman, C. Moore (2004). ''Finding community structure in very
           large networks.'' Phys. Rev. E 70.6 (2004).
           doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.

    .. hint::

        See :func:`~networkx_temporal.algorithms.multislice_modularity`
        and :func:`~networkx_temporal.algorithms.longitudinal_modularity`
        for temporal generalizations of the modularity metric, where
        the graph is sliced into snapshots or edge-leven events.

    .. seealso::

        The algorithm `documentation on NetworkX
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__
        for additional details on its implementation.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param partitions: List or dictionary with node partitions (i.e., communities). If a dictionary
        is provided, keys correspond to community indices and values to lists of nodes.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.

    :note: Wrapper function for
        `networkx.community.modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.
    """
    assert type(partitions) in (list, dict),\
        "Argument `partitions` must be a list or a dictionary."

    if is_temporal_graph(G):
        G = G.to_static()

    if type(partitions) == dict:
        partitions = list(partitions.values())

    # communities = list(partitions(G, attr=attr).values())

    return nx.algorithms.community.modularity(
        G, communities=partitions, weight=weight, resolution=resolution)
