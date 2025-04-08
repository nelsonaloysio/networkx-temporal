from typing import Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def brokering_centrality(
    G: Union[StaticGraph, TemporalGraph],
    clustering_coef: Optional[dict] = None,
) -> dict:
    """
    Returns brokering centrality of nodes.

    The brokering centrality of a node measures its degree of connectivity to its neighbors and is
    defined [8]_ as the product of the degree and the clustering coefficient of a node:

    .. math::

        \\text{bro}(i) = \\text{deg}(i) \\times \\text{clu}(i)

    where
    :math:`\\text{bro}(i)` is the brokering centrality of node :math:`i`,
    :math:`\\text{deg}` is the degree,
    and :math:`\\text{clu}` is the clustering coefficient.
    The brokering centrality is a measure of the node's ability to connect different parts of the
    network and is useful for identifying nodes that play a key role in the network's structure.

    .. [8] Cai, J.J., Borenstein, E., Petrov, D.A. (2010).
           Broker Genes in Human Disease.
           doi: `10.1093/gbe/evq064 <https://doi.org/10.1093/gbe/evq064>`_.

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    :param clustering_coef: Dictionary of precomputed clustering coefficient values. Optional.
    """
    degree_centrality = nx.degree_centrality(G)

    if not clustering_coef:
        clustering_coef = clustering_coefficient(G)

    return {
        node: degree_centrality[node] * clustering_coef[node]
        for node in G.nodes()
    }


def clustering_coefficient(G: Union[StaticGraph, TemporalGraph]) -> dict:
    """
    Returns clustering coefficient of nodes.

    Clustering coefficient measures the degree of interconnectivity in a node's neighborhood and is
    defined [8]_ [9]_ as the the number of edges between neighbors divided by the total number of
    possible edges between them. In undirected graphs, it may be calculated as:

    .. math::

        \\text{clu}(i) = \\frac{2n}{|N_i| \\, (|N_i| - 1)}

    where
    :math:`\\text{clu}(i)` is the clustering coefficient of node :math:`i`,
    :math:`n` is the number of edges between its neighbors,
    and :math:`|N_i|` is its number of neighbors.
    Lower values indicate nodes part of a loosely connected groups, while higher values indicate
    nodes at the center of fully connected clusters.

    .. [9] Watts, D.J., Strogatz, E. (1998).
           Collective dynamics of 'small-world' networks.
           Broker Genes in Human Disease.
           Nature.
           doi: `10.1038/30918 <https://doi.org/10.1038/30918>`_.

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    """
    clustering_coef = {
        node: sum(
            1
            for i in nx.neighbors(G, node)
            for j in nx.neighbors(G, node)
            if G.has_edge(i, j)
        ) / (len(list(G.neighbors(node))) * (len(list(G.neighbors(node))) - 1))
        for node in G.nodes()
    }

    return {
        node: clustering_coef[node] if clustering_coef[node] > 0 else 0
        for node in G.nodes()
    }