from typing import Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def clustering_coefficient(G: Union[StaticGraph, TemporalGraph]) -> dict:
    """
    Returns clustering coefficient of nodes.

    Clustering coefficient measures the degree of interconnectivity in a node's neighborhood and is
    defined [9]_ [11]_ as the the number of edges between neighbors divided by the total number of
    possible edges between them. In undirected graphs, it may be calculated as:

    .. math::

        \\text{clu}(i) = \\frac{2n}{|N_i| \\, (|N_i| - 1)}

    where
    :math:`\\text{clu}(i)` is the clustering coefficient of node :math:`i`,
    :math:`n` is the number of edges between its neighbors,
    and :math:`|N_i|` is its number of neighbors.
    Lower values indicate nodes part of a loosely connected groups, while higher values indicate
    nodes at the center of fully connected clusters.

    In temporal networks, clustering coefficient

    .. [11] Watts, D.J., Strogatz, E. (1998).
            Collective dynamics of 'small-world' networks.
            Broker Genes in Human Disease.
            Nature.
            doi: `10.1038/30918 <https://doi.org/10.1038/30918>`_.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
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
        node: clustering_coef[node] if clustering_coef.get(node, 0) > 0 else 0
        for node in G.nodes()
    }