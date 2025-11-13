from functools import reduce
from typing import Optional, Union

from networkx_temporal.classes.types import is_temporal_graph

from .modularity import modularity, _communities_dict
from ...typing import TemporalGraph


def multislice_modularity(
    TG: TemporalGraph,
    communities: Union[list, str, dict],
    resolution: Optional[float] = 1,
    interslice_weight: Optional[float] = 1,
    weight: Optional[str] = "weight",
    sparse: bool = False,
) -> float:
    """ Returns the MS-modularity of a temporal graph.

    Multislice modularity [10]_ is a generalization of the modularity measure for multiplex graphs,
    where each layer corresponds to a temporal graph snapshot. Temporal node copies are connected
    across time by interlayer edges (''couplings''), as in an
    `unrolled graph <../examples/convert.html#unrolled-temporal-graph>`__, so the expected fraction
    of intra-layer edges is adjusted to account for these added connections.
    It may be defined as:

    .. math::

        Q_{\\textnormal{MS}} =
        \\frac{1}{2 \\mu} \\sum_{G_t \\in \\mathcal{G}} \\left[ \\sum_{(i,j) \\in V^2}
        \\left( A_{ij} - \\gamma \\frac{d_i^{out} \\, d_j^{in}}{2m} \\delta(c_i, c_j) \\right)
        + \\sum_{i \\in V} \\omega \\, \\delta(c_{i}^{(t)}, c_{i}^{(t+1)}) \\right],

    where
    :math:`\\mu` is the total number of intra- and inter-layer edges in the temporal graph,
    :math:`G_t \\in \\mathcal{G}` are graph snapshots (slices/layers),
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`d` are node degrees,
    :math:`c` are their communities,
    and :math:`t` is the time or snapshot index.
    Additional term :math:`\\gamma = 1` (default) is the community resolution
    and :math:`\\omega = 1` (default) is the interlayer edge weight.

    .. [10] P. J. Mucha et al. (2010). ''Community Structure in Time-Dependent,
        Multiscale, and Multiplex Networks''. Science, 328, 876--878.
        doi: `10.1126/science.1184819 <https://doi.org/10.1126/science.1184819>`__.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param communities: List or dictionary with node memberships.
    :param resolution: The resolution parameter. Default is ``1``.
    :param interslice_weight: The interlayer edge weight. Default is ``1``.
    :param weight: The edge attribute key used to compute edge weights. Default: ``'weight'``.

    """
    interslice_weight = 1 if interslice_weight is None else interslice_weight

    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")

    Q = modularity(TG, communities, weight=weight, resolution=resolution, sparse=sparse)

    communities = [
        _communities_dict(G, communities[t] if type(communities[0]) == list else communities)
        for t, G in enumerate(TG)
    ]

    # Count node appearances over time.
    temporal_nodes = {}
    for G in TG:
        for node in G.nodes():
            temporal_nodes[node] = temporal_nodes.get(node, 0) + 1

    # Count total number of interslice edges.
    interslice_edges = sum(temporal_nodes[n] - 1 for n in temporal_nodes)

    # Count interslice edges within the same community.
    within_interslice_edges = sum(1
                                  for t in range(len(TG)-1) for n in TG[t].nodes()
                                  if communities[t][n] == communities[t+1].get(n, None))

    # Total number of edges (intra- + inter-slice).
    mu = sum(TG.size()) + interslice_edges

    # Combine intra- and inter-slice modularity contributions.
    Q_ms = (sum(Q) + (interslice_weight * within_interslice_edges)) / (2 * mu)

    return Q_ms
