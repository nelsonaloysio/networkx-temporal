from typing import Optional, Union

from ...typing import TemporalGraph
from ...utils import is_temporal_graph, partitions


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
    # raise NotImplementedError

    communities = list(partitions(G, attr=membership).values())

    m = TG.size()
    Q = 0

    for i, G in enumerate(TG):
        t = i if time is None else [
            t for (u, v), t in G.edges(data=time)
        ]
        communities_partitions = list(partitions(G, attr=communities).values())
        communities = list(partitions(G, attr=communities).values())

        # Iterate over the communities
        for community in communities:
            # Initialize the community modularity
            community_Q = 0

            # Iterate over the node pairs in the community
            for i in community:
                for j in community:
                    # Check if the nodes are connected
                    if TG.has_edge(i, j):
                        # Get the edge weight
                        if weight is not None:
                            edge_weight = TG.get_edge_data(i, j)[weight]
                        else:
                            edge_weight = 1

                        # Calculate the community modularity contribution
                        community_Q += edge_weight

                    # Calculate the null model contribution
                    community_Q -= (TG.degree(i) * TG.degree(j)) / (2 * m)

            # Add the community modularity to the total modularity
            Q += community_Q

    # Calculate the community switch count
    community_switch_count = 0
    for node in TG.nodes():
        # Get the community assignments for the node
        community_assignments = [community for community in communities if node in community]
        # Calculate the community switch count for the node
        community_switch_count += len(community_assignments) - 1

    # Penalize the modularity by the community switch count
    Q -= omega * community_switch_count / (2 * m)

    # Return the modularity
    return Q / (2 * m)

