from typing import List, Optional, Union

import networkx as nx

from .modularity_spectral import spectral_modularity
from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph
from ...utils import partitions


def modularity(
    TG: Union[StaticGraph, TemporalGraph],
    communities: Union[str, list, dict],
    resolution: Optional[float] = 1,
    weight: Optional[str] = "weight",
    sparse: Optional[bool] = True,
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

    If ``sparse=True`` (default), the modularity is computed using the spectral method [8]_
    instead:

    .. math::

        Q = \\frac{1}{2m} \\mathbf{C}^\\text{T} \\mathbf{B} \\mathbf{C},
        \\quad \\text{with} \\quad
        \\mathbf{B} = \\mathbf{A} - \\gamma
        \\frac{\\mathbf{d_{out}} \\, \\mathbf{d_{in}}^\\text{T}}{2m},

    where
    :math:`\\mathbf{B}` is the modularity matrix,
    :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix
    with :math:`n` as the number of nodes and :math:`k` the number of communities,
    :math:`m` is the total number of edges,
    and :math:`\\mathbf{d_{in}}` and :math:`\\mathbf{d_{out}}` are the node in- and out-degree
    vectors.
    If ``sparse=False``, use NetworkX's `modularity
    <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.multislice_modularity` function for a temporal
        generalization of the metric.

    .. [7] A. Clauset, M. E. J. Newman, C. Moore (2004). ''Finding community structure in very
        large networks.'' Phys. Rev. E 70.6 (2004).
        doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.

    .. [8] Newman, M. E. J. (2006). ''Modularity and community structure in networks''.
        Proceedings of the National Academy of Sciences, 103(23), 8577-8582.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param communities: String (node attribute name), list of community assignments,
        or list of such lists (for temporal graphs).
    :param resolution: The resolution parameter. Defaults to ``1``.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param sparse: Whether to use the sparse spectral method for modularity calculation.
        Default is ``True``.
    """
    resolution = 1 if resolution is None else resolution

    if not (is_temporal_graph(TG) or is_static_graph(TG)):
        raise TypeError(
            "Input must be a temporal or static NetworkX graph."
        )
    if type(communities) not in (str, list, dict):
        raise TypeError(
            "Argument `communities` must be a list of community assignments, "
            "a list of such lists (for temporal graphs), or a string (node attribute key)."
        )
    if is_static_graph(TG) and type(communities) == list and type(communities[0]) == list:
        raise ValueError(
            "For static graphs, `communities` must be a single list of community assignments."
        )
    if type(resolution) not in (int, float):
        raise TypeError("Resolution expects a numeric value.")
    if weight is not None and type(weight) != str:
        raise TypeError("Weight expects a string.")

    Q = [
        (spectral_modularity if sparse else _modularity)(
            G,
            communities=_communities_list(
                G, communities[t] if type(communities[0]) == list else communities),
            resolution=resolution,
            weight=weight,
        )
        for t, G in enumerate([TG] if is_static_graph(TG) else TG)
    ]

    return Q[0] if is_static_graph(TG) else Q


def _communities_dict(G, communities) -> dict:
    """ Converts community assignments to vector form.
    """
    if type(communities) == str:
        communities = {n: community for n, community in G.nodes(data=communities)}
    if type(communities) == list:
        communities = {n: communities[n] for n in range(G.order())}
    return communities


def _communities_list(G, communities) -> list:
    """ Converts community assignments to vector form.
    """
    if type(communities) == str:
        communities = [community for n, community in G.nodes(data=communities)]
    if type(communities) == dict:
        communities = [communities[n] for n in G.nodes()]
    communities_index = sorted(set(communities))
    communities = [communities_index.index(c) for c in communities]
    return communities


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
