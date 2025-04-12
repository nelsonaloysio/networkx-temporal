from typing import Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def bridging_centrality(
    G: Union[StaticGraph, TemporalGraph],
    betweenness: Optional[dict] = None,
    bridging_coef: Optional[dict] = None,
) -> dict:
    """
    Returns bridging centrality of nodes.

    Bridging centrality is a measure of the importance of a node in connecting
    different parts of a network, and is defined as the product of the betweenness
    centrality and the bridging coefficient:

    .. math::

        C_v^{Bdg} = C_v^{Btw} \\times BC_v

    where
    :math:`C_v^{Bdg}` is the bridging centrality of node :math:`v`,
    :math:`C_v^{Btw}` is the betweenness centrality of node :math:`v`, and
    :math:`BC_v` is the bridging coefficient of node :math:`v`.

    .. https://doi.org/10.1093/gbe/evq064
    .. https://cse.buffalo.edu/tech-reports/2006-05.pdf

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    :param betweenness: Dictionary of precomputed betweenness centrality values. Optional.
    :param bridging_coef: Dictionary of precomputed bridging coefficient values. Optional.
    """
    if not betweenness:
        betweenness = nx.betweenness_centrality(G)

    if not bridging_coef:
        bridging_coef = bridging_coef(G)

    return {
        node: betweenness[node] * bridging_coef[node]
        for node in G.nodes()
    }


@staticmethod
def bridging_coefficient(G: Union[StaticGraph, TemporalGraph]) -> dict:
    """
    Returns bridging coefficient of nodes.

    It is defined as the inverse degree of a node divided by the sum of the inverse degree of its
    neighbors:

    .. math::
        BC_v = \\frac{\\text{deg}_v^{-1}}{\\sum_{u \\in N_v} \\text{deg}_u^{-1}}

    where
    :math:`BC_v` is the bridging coefficient of node :math:`v`,
    :math:`N_v` is the set of neighbors of node :math:`v`, and
    :math:`d_u` is the degree of node :math:`u`.

    .. https://doi.org/10.1093/gbe/evq064
    .. https://cse.buffalo.edu/tech-reports/2006-05.pdf

    :param object G: :class:`~networkx_temporal.graph.TemporalGraph`
        or static NetworkX graph object.
    """
    sum_neigh_inv_deg = {
        node: sum((1/d) for d in [G.degree[n] for n in G.neighbors(node)])
        for node in G.nodes()
    }

    return {
        node: (1/G.degree[node]) / sum_neigh_inv_deg[node]
        if G.degree[node] > 0
        and sum_neigh_inv_deg[node] > 0
        else 0
        for node in G.nodes()
    }
