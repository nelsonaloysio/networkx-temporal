from typing import Optional, Union

import networkx as nx

from ...typing import StaticGraph, TemporalGraph
from ...utils import is_static_graph


def bridging_centrality(
    G: Union[TemporalGraph, StaticGraph],
    betweenness: Optional[dict] = None,
    bridging_coef: Optional[dict] = None,
) -> dict:
    """
    Returns bridging centrality of nodes.

    Bridging centrality measures the importance of a node in connecting different parts of a
    network, and is defined [7]_ as the product of betweenness centrality and bridging coefficient:

    .. math::

        c_{\\text{bri}}(i) = c_{\\text{bet}}(i) \\times \\text{bri}(i)

    where
    :math:`i` is a node,
    :math:`c_{\\text{bri}}` is the bridging centrality,
    :math:`c_{\\text{bet}}` is the betweenness centrality,
    and :math:`\\text{bri}` is the bridging coefficient.
    Returns zero for nodes with no neighbors.

    In temporal networks, brokering centrality is returned as a list of values, one per snapshot.

    .. [7] Hwang, W. et al. (2006).
           Bridging Centrality: Identifying Bridging Nodes In Scale-free Networks.
           https://cse.buffalo.edu/tech-reports/2006-05.pdf.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param betweenness: Dictionary of precomputed betweenness centrality values. Optional.
    :param bridging_coef: Dictionary of precomputed bridging coefficient values. Optional.
    """
    bridging_centrality = []

    for G in ([TG] if is_static_graph(TG) else TG):

        if not betweenness:
            betweenness = nx.betweenness_centrality(G)

        if not bridging_coef:
            bridging_coef = bridging_coefficient(G)

        bridging_centrality.append({
            node: betweenness[node] * bridging_coef[node]
            for node in G.nodes()
        })

    return bridging_centrality[0] if is_static_graph(TG) else bridging_centrality


def bridging_coefficient(TG: Union[TemporalGraph, StaticGraph]) -> dict:
    """
    Returns bridging coefficient of nodes.

    The bridging coefficient of a node measures the connectivity of its neighbors and is
    defined [7]_ as the inverse degree of the node divided by the sum of the inverse degrees of
    its neighbors:

    .. math::
        \\text{bri}(i) = \\frac{\\text{deg}(i)^{-1}}{\\sum_{j \\in N(i)} \\text{deg}(j)^{-1}}

    where
    :math:`i` is a node,
    :math:`\\text{bri}` is the bridging coefficient,
    :math:`\\text{deg}` is the degree,
    and :math:`j \\in N` is a node in the set of neighbors of node :math:`i`.
    Returns zero for nodes with no neighbors.

    In temporal networks, bridging coefficient is returned as a list of values, one per snapshot.

    :param object TG: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    bridging_coef = []

    for G in ([TG] if is_static_graph(TG) else TG):

        sum_neigh_inv_deg = {
            node: sum((1/d) for d in [G.degree[n] for n in G.neighbors(node)])
            for node in G.nodes()
        }

        bridging_coef.append({
            node: (1/G.degree[node]) / sum_neigh_inv_deg[node]
            if G.degree[node] > 0
            and sum_neigh_inv_deg[node] > 0
            else 0
            for node in G.nodes()
        })

    return bridging_coef[0] if is_static_graph(TG) else bridging_coef
