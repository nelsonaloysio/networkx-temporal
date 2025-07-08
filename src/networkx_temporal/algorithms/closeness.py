from typing import Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def closeness_centrality(G: Union[StaticGraph, TemporalGraph]) -> dict:
    """
    Returns temporal closeness centrality of nodes.

    Clsoeness centrality measures the degree of interconnectivity in a node's neighborhood and...

    .. math::

        \\text{clu}(i) = \\frac{2n}{|N_i| \\, (|N_i| - 1)}

    where
    :math:`\\text{clo}(i)` is the closeness centrality of node :math:`i`,

    In temporal networks, closeness coefficient

    .. [11] Watts, D.J., Strogatz, E. (1998).
            Collective dynamics of 'small-world' networks.
            Broker Genes in Human Disease.
            Nature.
            doi: `10.1038/30918 <https://doi.org/10.1038/30918>`_.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    closeness_coef = {
        node: sum(
            1
            for i in nx.neighbors(G, node)
            for j in nx.neighbors(G, node)
            if G.has_edge(i, j)
        ) / (len(list(G.neighbors(node))) * (len(list(G.neighbors(node))) - 1))
        for node in G.nodes()
    }

    return {
        node: closeness_coef[node] if closeness_coef.get(node, 0) > 0 else 0
        for node in G.nodes()
    }