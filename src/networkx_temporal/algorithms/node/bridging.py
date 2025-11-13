from typing import List, Optional, Union

from ...classes.types import is_static_graph
from ...typing import StaticGraph, TemporalGraph


def bridging_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    betweenness: Optional[Union[dict, List[dict]]] = None,
) -> Union[dict, List[dict]]:
    """ Returns bridging centrality of nodes.

    Bridging centrality measures the importance of a node in connecting different parts of a
    network, and is defined [2]_ as the product of betweenness centrality and bridging coefficient:

    .. math::

        c_{\\text{bri}}(i) = c_{\\text{bet}}(i) \\times \\text{bri}(i),

    where :math:`c_{\\text{bet}}(i)` is the betweenness centrality of node :math:`i`,
    and :math:`\\text{bri}(i)` its bridging coefficient, i.e.,

    .. math::

        \\text{bri}(i) = \\frac{\\text{deg}(i)^{-1}}{\\sum_{j \\in N(i)} \\text{deg}(j)^{-1}},

    being :math:`\\text{deg}(i)^{-1}` the inverse degree of node :math:`i`, and :math:`N(i)` its
    set of neighbors :math:`j \\in N(i)`.

    Returns zero for isolated nodes, i.e., with no neighbors.
    If ``betweenness`` is not provided, the bridging coefficient of nodes is returned instead,
    that is, consider :math:`c_{\\text{bet}}(i) = 1` for all nodes.

    .. [2] Hwang, W. et al. (2006).
        ''Bridging Centrality: Identifying Bridging Nodes In Scale-free Networks''.
        url: `cse.buffalo.edu/tech-reports/2006-05.pdf
        <https://cse.buffalo.edu/tech-reports/2006-05.pdf>`__.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param betweenness: Dictionary of node betweenness centrality values. Returns
        bridging coefficient if not provided. Optional.
    """
    bridging_centrality = []

    for G in ([TG] if is_static_graph(TG) else TG):
        # Bridging coefficient.
        sum_neigh_inv_deg = {
            node: sum(1/G.degree[n] for n in G.neighbors(node))
            for node in G.nodes()
        }
        coef = {
            node: (1/G.degree[node]) / sum_neigh_inv_deg[node]
            if G.degree[node] > 0
            and sum_neigh_inv_deg[node] > 0
            else 0
            for node in G.nodes()
        }
        # Bridging centrality, if betweenness is provided.
        centrality = {
            node: (betweenness[node] if betweenness is not None else 1) * coef[node]
            for node in G.nodes()
        }
        # Normalize to [0, 1] range.
        max_centrality = max(centrality.values()) if centrality else 1
        if max_centrality > 0:
            centrality = {node: centrality[node] / max_centrality for node in G.nodes()}
        bridging_centrality.append(centrality)

    return bridging_centrality[0] if is_static_graph(TG) else bridging_centrality
