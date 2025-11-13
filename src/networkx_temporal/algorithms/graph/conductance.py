from typing import List, Optional, Union

import networkx as nx

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph
from ...utils import map_attr_to_nodes, partition_nodes


def conductance(
    TG: Union[TemporalGraph, StaticGraph],
    communities: Union[str, list, dict],
    weight: Optional[str] = "weight",
) -> Union[float, List[float]]:
    """ Returns the conductance of a graph.

    Conductance [6]_ measures the fraction of edges that falls within a community compared to
    those leaving it. Lower values indicate well-defined internal community structures,
    weakly connected to the rest of the graph. For a set of communities, it is defined as their
    average:

    .. math::

        \\phi(G, C) = \\frac {\\sum_{S \\in C} \\min_{S \\subseteq V} \\phi (S)} {|C|},

    where :math:`G` is a graph,
    :math:`C` is a set of disjoint node partitions,
    :math:`V` is the set of all nodes,
    and :math:`\\phi(S)` is the conductance of each node subset :math:`S \\in C`.
    The latter is defined as:

    .. math::

        \\phi(S) = \\frac{\\text{cut}(S, \\bar{S})}{\\min(\\text{vol}(S), \\text{vol}(\\bar{S}))},

    where :math:`\\text{cut}(S, \\bar{S})` is the total weight of edges connecting :math:`S`
    to its complement :math:`\\bar{S}`,
    and :math:`\\text{vol}(S)` is the volume of :math:`S`, i.e., the total weight of all edges
    starting at the node subset.

    .. [6] Kannan, R., Vempala, S., & Vetta, A. (2004). ''On clusterings: Good, bad and spectral''.
        Journal of the ACM (JACM), 51(3), 497-515.
        doi: `10.1145/990308.990313 <https://doi.org/10.1145/990308.990313>`__.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param communities: List of community assignments for each node, or
        a list of lists in case of temporal graphs, one per snapshot.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :note: Wrapper around NetworkX's
        `conductance <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.cuts.conductance.html>`__
        function.
    """
    if not is_static_graph(TG) and not is_temporal_graph(TG):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_static_graph(TG):
        subsets = partition_nodes(TG, communities, index=False)
        return sum(nx.algorithms.conductance(TG, S=S, weight=weight) for S in subsets
                   ) / len(subsets)

    assignments = map_attr_to_nodes(TG, communities)
    return [conductance(G, z) for G, z in zip(TG, assignments)]
