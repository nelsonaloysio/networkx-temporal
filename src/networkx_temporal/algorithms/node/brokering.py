from typing import List, Optional, Union

import networkx as nx

from ...classes.types import is_static_graph
from ...typing import StaticGraph, TemporalGraph


def brokering_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    clustering_coef: Optional[Union[dict, List[dict]]] = None,
) -> Union[dict, List[dict]]:
    """ Returns brokering centrality of nodes.

    Brokering centrality [3]_ is a measure of the node's ability to connect different parts of the
    network and is useful for identifying nodes that play a key role in the network's structure.
    It is defined as:

    .. math::

        \\text{bro}(i) = \\text{deg}(i) \\times \\text{clu}(i),

    where
    :math:`\\text{deg}(i)` is the degree centrality of node :math:`i`,
    and :math:`\\text{clu}(i)` is its clustering coefficient.

    Clustering coefficient works as a measure of interconnectivity in a node's neighborhood and may
    be defined [4]_ as the the number of edges between a node's neighbors divided by the
    number of possible edges between them. If ``clustering_coef`` is not provided, it is computed
    as:

    .. math::

        \\text{clu}(i) = \\frac{2n}{|N_i| \\, (|N_i| - 1)},

    where
    :math:`\\text{clu}(i)` is the clustering coefficient of node :math:`i`,
    :math:`n` is the number of edges between its neighbors,
    and :math:`|N_i|` is its number of neighbors.
    Lower values indicate nodes part of a loosely connected groups, while higher values indicate
    nodes at the center of fully connected clusters.

    .. attention::

        In directed graphs, connections are not necessarily reciprocal, affecting the coefficients.

    .. [3] Cai, J.J., Borenstein, E., Petrov, D.A. (2010).
        ''Broker Genes in Human Disease''.
        Genome Biology and Evolution, 2.
        doi: `10.1093/gbe/evq064 <https://doi.org/10.1093/gbe/evq064>`_.

    .. [4] Watts, D.J., Strogatz, E. (1998).
        ''Collective dynamics of 'small-world' networks''.
        Nature.
        doi: `10.1038/30918 <https://doi.org/10.1038/30918>`_.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param clustering_coef: Dictionary of precomputed clustering coefficient values. Optional.
    """
    brokering_centrality = []

    for t, G in enumerate([TG] if is_static_graph(TG) else TG):
        degree_centrality = nx.degree_centrality(G)
        # Clustering coefficient.
        coef = clustering_coef
        if coef is None:
            coef = {
                node: (
                    sum(
                        1
                        for i in nx.neighbors(G, node)
                        for j in nx.neighbors(G, node)
                        if G.has_edge(i, j)
                    ) /
                    ((len(list(G.neighbors(node))) * (len(list(G.neighbors(node))) - 1)) or 1)
                )
                or 0
                for node in G.nodes()
            }
        elif type(coef) == list:
            coef = coef[t]
        # Brokering centrality.
        centrality = {
            node: degree_centrality[node] * coef[node]
            for node in G.nodes()
        }
        # Normalize to [0, 1] range.
        max_centrality = max(centrality.values()) if centrality else 1
        if max_centrality > 0:
            centrality = {node: centrality[node] / max_centrality for node in G.nodes()}
        brokering_centrality.append(centrality)

    return brokering_centrality[0] if is_static_graph(TG) else brokering_centrality
