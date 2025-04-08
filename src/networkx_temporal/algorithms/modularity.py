from typing import Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph
from ..utils import is_temporal_graph, partitions, to_multigraph


def modularity(
    G: Union[StaticGraph, TemporalGraph],
    membership: Union[str, list, dict],
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
    :param membership: List, dictionary, or node attribute key with the community assignment.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.

    :note: Wrapper function for
        `networkx.community.modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.
    """
    if is_temporal_graph(G):
        G = to_multigraph(G).to_static()

    communities = list(partitions(G, attr=membership).values())

    return nx.algorithms.community.modularity(
        G, communities=communities, weight=weight, resolution=resolution)



def longitudinal_modularity(
    TG: TemporalGraph,
    membership: Union[str, list, dict],
    time: Optional[str] = None,
    weight: Optional[str] = "weight",
    resolution: float = 1,
    omega: float = 1,
) -> float:
    """
    Returns the L-modularity of a temporal graph.

    Longitudinal modularity [6]_ is a generalization of the metric for temporal graphs, which adds
    a smoothness term to penalize nodes switching communities and the membership expectation
    for the lifetimes of pairs of nodes in the same community in a null model. It is defined as:

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

    .. [6] V. Brabant et al (2025). ''Longitudinal modularity, a modularity for
           link streams.'' EPJ Data Science, 14, 12.
           doi: `10.1140/epjds/s13688-025-00529-x <https://doi.org/10.1140/epjds/s13688-025-00529-x>`__.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param omega: The interlayer edge weight. Default is ``1``.
    """
    assert is_temporal_graph(TG), "Graph must be a temporal graph."

    communities = list(partitions(G, attr=membership).values())

    # m = TG.size()
    # Q = 0

    # for i, G in enumerate(TG):
    #     t = i if time is None else [
    #         t for (u, v), t in G.edges(data=time)
    #     ]
    #     communities_partitions = list(partitions(G, attr=communities).values())
    #     communities = list(partitions(G, attr=communities).values())

    #     # Iterate over the communities
    #     for community in communities:
    #         # Initialize the community modularity
    #         community_Q = 0

    #         # Iterate over the node pairs in the community
    #         for i in community:
    #             for j in community:
    #                 # Check if the nodes are connected
    #                 if TG.has_edge(i, j):
    #                     # Get the edge weight
    #                     if weight is not None:
    #                         edge_weight = TG.get_edge_data(i, j)[weight]
    #                     else:
    #                         edge_weight = 1

    #                     # Calculate the community modularity contribution
    #                     community_Q += edge_weight

    #                 # Calculate the null model contribution
    #                 community   _Q -= (TG.degree(i) * TG.degree(j)) / (2 * m)

    #         # Add the community modularity to the total modularity
    #         Q += community_Q

    # # Calculate the community switch count
    # community_switch_count = 0
    # for node in TG.nodes():
    #     # Get the community assignments for the node
    #     community_assignments = [community for community in communities if node in community]
    #     # Calculate the community switch count for the node
    #     community_switch_count += len(community_assignments) - 1

    # # Penalize the modularity by the community switch count
    # Q -= omega * community_switch_count / (2 * m)

    # # Return the modularity
    # return Q / (2 * m)


def multislice_modularity(
    TG: TemporalGraph,
    communities: Union[str, list, dict],
    weight: Optional[str] = "weight",
    resolution: float = 1,
    omega: float = 1,
) -> float:
    """
    Returns the MS-modularity of a temporal graph.

    Multislice modularity [5]_ is a generalization of the modularity measure for multiplex graphs.
    In case of temporal networks, each layer corresponds to a temporal graph snapshot. Temporal
    node copies are connected across time by interlayer edges (''couplings''), as in a
    `unrolled graph <../examples/convert.html#unrolled-temporal-graph>`__, so the expected fraction
    of intra-layer edges is adjusted to account for these added connections:

    .. math::

        Q_{\\textnormal{MS}} =
        \\frac{1}{2 \\mu} \\sum_{G_t \\in \\mathcal{G}} \\left[ \\sum_{(i,j) \\in V^2}
        \\left( \\mathbf{A}_{ij} - \\gamma \\frac{k_i k_j}{2m} \\delta(c_i, c_j) \\right)
        + \\sum_{i \\in V} \\omega_i^{(t)} \\, \\delta(c_{i}^{(t)}, c_{i}^{(t+1)}) \\right],

    where
    :math:`\\mu` is the number of (undirected) edges in the temporal graph,
    :math:`G_t \\in \\mathcal{G}` are graphs snapshots (slices/layers),
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`k` are node degrees,
    :math:`c` are their communities,
    and :math:`t` is the time or snapshot index.
    Aditional term :math:`\\gamma = 1` (default) is the community resolution
    and :math:`\\omega = 1` (default) is the interlayer edge weight.

    .. [5] P. J. Mucha et al. (2010). ''Community Structure in Time-Dependent,
           Multiscale, and Multiplex Networks''. Science, 328, 876--878.
           doi: `10.1126/science.1184819 <https://doi.org/10.1126/science.1184819>`__.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param membership: List, dictionary, or node attribute key with the community assignment.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param omega: The interlayer edge weight. Default is ``1``.
    """
    assert is_temporal_graph(TG), "Graph must be a temporal graph."

    # m = TG.number_of_edges()
    # Q = 0

    # # Iterate over the communities
    # community = {
    #     node: [G.nodes[node][attr] for G in TG if G.has_node(node)] for node in G.nodes()
    # }

    # community = {}
    # for G in TG:
    #     for node in G.nodes():
    #         # Get the community assignment for the node
    #         community[node] = community.get(node, []) + [G.nodes[node]['community']]

    # for community in communities:
    #     # Initialize the community modularity
    #     community_modularity = 0

    #     # Iterate over the node pairs in the community
    #     for i in community:
    #         for j in community:
    #             # Check if the nodes are connected
    #             if TG.has_edge(i, j):
    #                 # Get the edge weight
    #                 if weight is not None:
    #                     edge_weight = TG.get_edge_data(i, j)[weight]
    #                 else:
    #                     edge_weight = 1

    #                 # Calculate the community modularity
    #                 community_modularity += edge_weight

    #                 # Calculate the geometric mean of the lifetimes of the nodes
    #                 lifetime_i = len([t for t in TG.nodes[i]['times'] if i in community])
    #                 lifetime_j = len([t for t in TG.nodes[j]['times'] if j in community])
    #                 geometric_mean = np.sqrt(lifetime_i * lifetime_j) / len(TG.nodes[i]['times'])

    #                 # Calculate the community modularity
    #                 community_modularity -= (TG.degree(i) * TG.degree(j)) / (2 * m) * geometric_mean

    #     # Add the community modularity to the total modularity
    #     Q += community_modularity

    # # Calculate the community switch count
    # community_switch_count = 0
    # for node in TG.nodes():
    #     community_switch_count += len([t for t in TG.nodes[node]['times'] if node in communities]) - 1

    # # Penalize the modularity by the community switch count
    # Q -= omega * community_switch_count / (2 * m)

    # # Return the longitudinal modularity
    # return Q / (2 * m)
