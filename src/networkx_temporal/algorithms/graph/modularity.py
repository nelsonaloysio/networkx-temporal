from typing import List, Optional, Union

import networkx as nx

from .modularity_spectral import spectral_modularity
from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph
from ...utils import partitions


def modularity(
    TG: Union[TemporalGraph, StaticGraph],
    communities: Union[str, list, dict],
    resolution: Optional[float] = 1,
    weight: Optional[str] = "weight",
    sparse: bool = False
) -> Union[float, List[float]]:
    """ Returns the modularity of a graph.

    Modularity [7]_ measures the fraction of edges in a graph that fall within communities,
    compared to their expected number in a random graph with the same degree sequence.
    Higher values may indicate more internal connections than expected by chance.
    It is commonly defined as:

    .. math::

        Q =
        \\frac{1}{2m} \\sum_{(i,j) \\in V^2}
        \\left[ A_{ij} - \\gamma \\frac{d_i^{out} \\, d_j^{in}}{2m} \\right]
        \\delta(c_i, c_j),

    where
    :math:`m` is the number of edges in the graph,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`d` are node in/out-degrees,
    :math:`c` are their communities,
    and :math:`\\gamma = 1` (default) is the resolution parameter [4]_,
    where smaller values favor larger communities, including negative values.

    This can be reduced to a summation over communities, which is more efficient to compute:

    .. math::

        Q = \\sum_{c \\in C} \\left[ \\frac{L_c}{m} - \\gamma
        \\left( \\frac{d_c}{2m} \\right)^2 \\right],

    where :math:`L_c` is the number of within-community edges
    and :math:`d_c` is the sum of degrees of nodes in community :math:`c`.
    If ``sparse=True``, modularity is computed using
    :func:`~networkx_temporal.algorithms.spectral_modularity` instead.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.modularity_multislice` function for a temporal
        generalization of the metric.

    .. [7] A. Clauset, M. E. J. Newman, C. Moore (2004). ''Finding community structure in very
        large networks.'' Phys. Rev. E 70.6 (2004).
        doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param communities: String (node attribute name), list of community assignments,
        or list of such lists (for temporal graphs).
    :param resolution: The resolution parameter. Defaults to ``1``.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param sparse: Whether to use the sparse spectral method for modularity calculation.
        Default is ``True``.

    :note: If ``sparse=False``, use NetworkX's `modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__
        function.
    """
    resolution = 1 if resolution is None else resolution
    multi_assign = True if type(communities) == list and type(communities[0]) == list else False

    if type(communities) not in (str, list, dict):
        raise TypeError(
            "Argument `communities` must be a list of community assignments, "
            "a list of such lists (for temporal graphs), or a string (node attribute name)."
        )
    if not is_static_graph(TG) and not is_temporal_graph(TG):
        raise TypeError(
            "Input must be a temporal or static NetworkX graph."
        )
    if is_static_graph(TG) and multi_assign:
        raise ValueError(
            "For static graphs, `communities` does not accept a list of lists."
        )
    if type(resolution) not in (int, float):
        raise TypeError("Resolution expects a numeric value.")
    if weight is not None and type(weight) != str:
        raise TypeError("Weight expects a string.")

    Q = [
        (modularity_spectral if sparse else _modularity)(
            G,
            communities=_node_attr_to_list(
                G, communities[t] if type(next(iter(communities))) == list else communities),
            resolution=resolution,
            weight=weight,
        )
        for t, G in enumerate([TG] if is_static_graph(TG) else TG)
    ]

    return Q[0] if is_static_graph(TG) else Q


def _modularity(G, communities, resolution, weight) -> float:
    """ Calculates modularity using NetworkX's built-in function.
    """
    communities = partitions(G, communities).values()
    return nx.algorithms.community.modularity(
        G,
        communities=communities,
        resolution=resolution,
        weight=weight,
    )


def _node_attr_to_dict(G, attr) -> dict:
    """ Converts node attributes to dict form.
    """
    if type(attr) == str:
        attr = {n: community for n, community in G.nodes(data=attr)}
    if type(attr) == list:
        attr = {n: attr[n] for n in range(G.order())}
    return attr


def _node_attr_to_list(G, attr) -> list:
    """ Converts node attributes to list form.
    """
    if type(attr) == str:
        attr = [community for n, community in G.nodes(data=attr)]
    if type(attr) == dict:
        attr = [attr[n] for n in G.nodes()]
    attr_index = sorted(set(attr))
    attr = [attr_index.index(c) for c in attr]
    return attr
