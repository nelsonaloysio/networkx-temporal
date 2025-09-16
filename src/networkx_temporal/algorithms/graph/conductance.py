from typing import Optional, Union

import networkx as nx

from ...typing import StaticGraph, TemporalGraph
from ...utils import is_temporal_graph, partitions


def conductance(
    G: Union[StaticGraph, TemporalGraph],
    partitions: Union[list, dict],
    weight: Optional[str] = "weight",
    subsets: bool = False,
) -> float:
    """
    Returns the conductance of a graph or its subsets.

    Conductance [10]_ measures the fraction of edges that falls within community boundaries, that is,
    the ratio of connections leaving a community compared to its total degree.
    It is defined as:

    .. math::

        \\phi(G) = \\min_{S \\subseteq V} \\phi (S),

    where :math:`S` is a subset of nodes in the graph (i.e., a community) and :math:`V` is the set
    of all nodes.
    Meanwhile, the conductance of a subset of nodes :math:`S` is given by the cut size ratio:

    .. math::

        \\phi(S) = \\frac{\\text{cut}(S, \\bar{S})}{\\min(\\text{vol}(S), \\text{vol}(\\bar{S}))},

    where :math:`\\text{cut}(S, \\bar{S})` is the total weight of edges connecting :math:`S`
    to its complement :math:`\\bar{S}`,
    and :math:`\\text{vol}(S)` is the volume of :math:`S`, i.e., the total weight of all edges
    starting at the (disjoint) node subset.

    A lower conductance value describes well-defined internal community structures, while a higher
    value indicates weakly connected components within. Note that conductance is susceptible
    to the resolution limit when communities are small, tending to favor larger groups of nodes.

    .. [10] Kannan, R., Vempala, S., & Vetta, A. (2004). ''On clusterings: Good, bad and spectral''.
           Journal of the ACM (JACM), 51(3), 497-515.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param partitions: List or dictionary with node partitions (i.e., communities). If a dictionary
        is provided, keys correspond to community indices and values to lists of nodes.
    :param weight: The edge attribute key used to compute edge weights. If ``None`` (default),
        all edge weights are considered as ``1``.
    :param subsets: If ``True``, returns the conductance of each subset in ``partitions``.
        Default is ``False``.
    """
    assert type(partitions) in (list, dict),\
        "Argument `partitions` must be a list or a dictionary."

    if is_temporal_graph(G):
        G = G.to_static()

    if type(partitions) == dict:
        partitions = list(partitions.values())

    # if type(partitions) == str:
    #     communities = list(partitions(G, attr=attr).values())

    raise NotImplementedError
