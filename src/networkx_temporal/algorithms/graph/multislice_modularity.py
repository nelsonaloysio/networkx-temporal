from typing import Optional, Union

from ...typing import TemporalGraph
from ...utils import is_temporal_graph, partitions


def multislice_modularity(
    TG: TemporalGraph,
    communities: Union[str, list, dict],
    weight: Optional[str] = "weight",
    resolution: float = 1,
    omega: float = 1,
) -> float:
    """
    Returns the MS-modularity of a temporal graph.

    Multislice modularity [5]_ is a generalization of the modularity measure for multiplex graphs,
    where each layer corresponds to a temporal graph snapshot. Temporal node copies are connected
    across time by interlayer edges (''couplings''), as in a
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
    # raise NotImplementedError

    m = TG.number_of_edges()
    Q = 0

    # Iterate over the communities
    community = {
        node: [G.nodes[node][attr] for G in TG if G.has_node(node)] for node in G.nodes()
    }

    community = {}
    for G in TG:
        for node in G.nodes():
            # Get the community assignment for the node
            community[node] = community.get(node, []) + [G.nodes[node]['community']]

    for community in communities:
        # Initialize the community modularity
        community_modularity = 0

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

                    # Calculate the community modularity
                    community_modularity += edge_weight

                    # Calculate the geometric mean of the lifetimes of the nodes
                    lifetime_i = len([t for t in TG.nodes[i]['times'] if i in community])
                    lifetime_j = len([t for t in TG.nodes[j]['times'] if j in community])
                    geometric_mean = np.sqrt(lifetime_i * lifetime_j) / len(TG.nodes[i]['times'])

                    # Calculate the community modularity
                    community_modularity -= (TG.degree(i) * TG.degree(j)) / (2 * m) * geometric_mean

        # Add the community modularity to the total modularity
        Q += community_modularity

    # Calculate the community switch count
    community_switch_count = 0
    for node in TG.nodes():
        community_switch_count += len([t for t in TG.nodes[node]['times'] if node in communities]) - 1

    # Penalize the modularity by the community switch count
    Q -= omega * community_switch_count / (2 * m)

    # Return the longitudinal modularity
    return Q / (2 * m)
