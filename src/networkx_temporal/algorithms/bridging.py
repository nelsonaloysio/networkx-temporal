from typing import Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph
from ..utils import is_static_graph


def bridging_centrality(
    G: Union[StaticGraph, TemporalGraph],
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

    In temporal networks, bridging centrality considers the temporal betweenness centrality
    defined in [8]_, calculated with
    :func:`~networkx_temporal.algorithms.betweenness_centrality`. This behavior can be overriden
    by passing a dictionary ``betweenness`` with the defined values for each node.

    .. [7] Hwang, W. et al. (2006).
           Bridging Centrality: Identifying Bridging Nodes In Scale-free Networks.
           https://cse.buffalo.edu/tech-reports/2006-05.pdf.

    .. [8]

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param betweenness: Dictionary of precomputed betweenness centrality values. Optional.
    :param bridging_coef: Dictionary of precomputed bridging coefficient values. Optional.
    """
    if not betweenness:
        betweenness = nx.betweenness_centrality(G)

    if not bridging_coef:
        bridging_coef = bridging_coefficient(G)

    return {
        node: betweenness[node] * bridging_coef[node]
        for node in G.nodes()
    }


def bridging_coefficient(G: Union[StaticGraph, TemporalGraph]) -> dict:
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

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
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
