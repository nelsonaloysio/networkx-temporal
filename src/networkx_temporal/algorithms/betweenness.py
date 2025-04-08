from typing import Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph
from ..utils import is_static_graph


def betweenness_centrality(
    G: Union[StaticGraph, TemporalGraph],
    k: Optional[int] = None,
    normalized: bool = True,
    weight: Optional[str] = None,
    endpoints: bool = False,
    seed: Optional[int] = None,
) -> dict:
    """
    Returns betweenness centrality of nodes.

    Betweenness measures the fraction of all-pairs shortest paths that pass through a
    node, i.e.

    .. math::

        c_{\\text{bet}}(i) = \\sum_{s,t \\in V} \\frac{\\sigma(s,t|v)}{\\sigma(s,t)}

    where
    :math:`i` is a node,
    :math:`c_{\\text{bet}}` is the betweenness centrality,
    :math:`V` is the set of nodes,
    :math:`\\sigma(s,t)` is the number of shortest paths from node :math:`s` to node :math:`t`,
    :math:`\\sigma(s,t|v)` is the number of those paths that pass through some node :math:`v`
    other than :math:`s` or :math:`t`.
    If :math:`s = t`, :math:`\\sigma(s,t) = 0` and :math:`\\sigma(s,t|v) = 0` for all :math:`v`.

    In temporal networks, betweenness centrality considers...

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    if is_static_graph(G):
        return nx.betweenness_centrality(G, k=k, normalized=normalized, weight=weight,
                                         endpoints=endpoints, seed=seed)

    raise NotImplementedError
