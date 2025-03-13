from typing import Any, Optional, Union

import networkx as nx

from ...typing import StaticGraph, TemporalGraph


def modularity(
    G: Union[StaticGraph, TemporalGraph],
    weight: Optional[str] = None,
    resolution: float = 1,
) -> float:
    """
    Returns the modularity of a graph.

    Modularity [1]_ measures the fraction of edges in a graph that fall within communities,
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
    where larger values favor smaller communities [2]_.
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

    .. attention::

        This version of the metric considers a static graph. For alternatives that handle
        temporal graphs, see :func:`~networkx_temporal.metrics.community.longitudinal_modularity`
        and :func:`~networkx_temporal.metrics.community.multislice_modularity`.

    .. seealso::

        The algorithm `documentation on NetworkX
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__
        for additional details on its implementation.

    :param G: A NetworkX graph or temporal graph.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.

    :note: Wrapper function for
        `networkx.community.modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.

    .. [1] Mark Newman (2018). ''Networks''. Oxford University Press, 2nd ed., pp. 498--514.

    .. [2] A. Clauset, M. E. J. Newman, C. Moore (2004). ''Finding community structure in very
           large networks.'' Phys. Rev. E 70.6 (2004).
           doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.
    """
    return nx.algorithms.community.modularity(TG.flatten(), weight=weight, resolution=resolution)


def longitudinal_modularity(
    TG: TemporalGraph,
    weight: Optional[str] = None,
    resolution: float = 1,
    omega: float = 1,
) -> float:
    """
    Returns the L-modularity of a temporal graph.

    Longitudinal modularity [3]_ is a generalization of the metric for temporal graphs, which adds
    a smoothness term to penalize nodes that switch communities over time and abstracts away the
    need to slice the graph into snapshots (unlike
    :func:`~networkx_temporal.metrics.community.multislice_modularity`).
    It is defined as:

    .. math::

        Q_{\\textnormal{L}} =
        \\frac{1}{2m} \\sum_{C \\in \\mathcal{G}} \\left[ \\sum_{(i,j) \\in V^2}
        \\mathbf{A}_{ij} \\, \\delta(c_i, c_j)  - \\frac{k_i k_j}{2m}
        \\frac{\\sqrt{|T_{i \\in V_C}| |T_{j \\in V_C}|}}{|T|} \\right]
        - \\frac{\\omega}{2m} \\sum_{i \\in V} \\eta_i,

    where
    :math:`m` is the number of (undirected) edges in the graph,
    :math:`C \\in \\mathcal{G}` are all of its communities,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`k` are node degrees,
    :math:`T` is the set of all snapshots,
    :math:`\\omega = 1` (default) is a smoothing parameter,
    and :math:`\\eta` is the community switch count of a node,
    equivalent to the number of times it joins (or rejoins) a community minus one.

    Temporal dynamics are considered by including (inside brackets) the geometric mean of the
    lifetimes of pairs of nodes in the same community, normalized by the total number of snapshots,
    as a measure of ''mean membership expectation''. This term is therefore bounded by zero, if two
    nodes are never in the same community, and one, if they are always together.

    Lastly, modularity is penalized by the number of community switches, which is adjusted by the
    smoothing parameter :math:`\\omega = 1` (default), with larger values resulting in a stronger
    penalty.

    :param TG: A NetworkX temporal graph.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param omega: The interlayer edge weight. Default is ``1``.

    .. [3] V. Brabant et al (2025). ''Longitudinal modularity, a modularity for
           link streams.'' EPJ Data Science, 14, 12.
           doi: `10.1140/epjds/s13688-025-00529-x <https://doi.org/10.1140/epjds/s13688-025-00529-x>`__.
    """
    pass


def multislice_modularity(
    TG: TemporalGraph,
    weight: Optional[str] = None,
    resolution: float = 1,
    omega: float = 1,
) -> float:
    """
    Returns the MS-modularity of a temporal graph.

    Multislice modularity [4]_ is a generalization of the modularity measure for multiplex graphs.
    In case of temporal networks, each layer corresponds to a temporal graph snapshot. Temporal
    node copies are connected across time by interlayer edges (''couplings''), as in a
    `unified graph <../examples/convert.html#unified-temporal-graph>`__, so the expected fraction
    of intra-layer edges is adjusted to account for these added connections:

    .. math::

        Q_{\\textnormal{MS}} =
        \\frac{1}{2 \\mu} \\sum_{G \\in \\mathcal{G}} \\left[ \\sum_{(i,j) \\in V^2}
        \\left( \\mathbf{A}_{ij} - \\gamma \\frac{k_i k_j}{2m} \\delta(c_i, c_j) \\right)
        + \\sum_{i \\in V} \\omega_i^{(t)} \\, \\delta(c_{i}^{(t)}, c_{i}^{(t+1)}) \\right],

    where
    :math:`\\mu` is the number of (undirected) edges (including couplings) in the graph,
    :math:`G \\in \\mathcal{G}` are graphs snapshots (slices/layers),
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`k` are node degrees,
    :math:`c` are their communities,
    :math:`t` is the time step or snapshot index,
    :math:`\\gamma = 1` (default) is the resolution parameter,
    and :math:`\\omega \\in \\{0, 1\\}` (default) is the interlayer edge weight,
    which is zero if the same node either disappears or is in different communities in the
    consecutive snapshot.

    :param TG: A NetworkX temporal graph.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param omega: The interlayer edge weight. Default is ``1``.

    .. [4] P. J. Mucha et al. (2010). ''Community Structure in Time-Dependent,
           Multiscale, and Multiplex Networks''. Science, 328, 876--878.
           doi:`10.1126/science.1184819 <https://doi.org/10.1126/science.1184819>`__.
    """
    pass


# Q_{\\textnormal{MS}} =
# \\frac{1}{2\\mu} \\sum_{ijsr} \\left[
# \\left( \\mathbf{A}_{ijs} - \\gamma_s \\frac{k_i k_j}{2m} \\right)
# \\delta_{sr} + \\delta_{ij} \, C_{jsr} \\right] \\delta(g_{is}, g_{jr}),
# \{ V^{(t)} \\cap V^{(t+1)}