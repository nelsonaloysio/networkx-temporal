from typing import Optional, Union

import networkx as nx

from .clustering import clustering_coefficient
from ..typing import StaticGraph, TemporalGraph


def brokering_centrality(
    G: Union[StaticGraph, TemporalGraph],
    clustering_coef: Optional[dict] = None,
) -> dict:
    """
    Returns brokering centrality of nodes.

    The brokering centrality of a node measures its degree of connectivity to its neighbors and is
    defined [9]_ as the product of the degree and the clustering coefficient of a node:

    .. math::

        \\text{bro}(i) = \\text{deg}(i) \\times \\text{clu}(i)

    where
    :math:`\\text{bro}(i)` is the brokering centrality of node :math:`i`,
    :math:`\\text{deg}` is the degree,
    and :math:`\\text{clu}` is the clustering coefficient.
    The brokering centrality is a measure of the node's ability to connect different parts of the
    network and is useful for identifying nodes that play a key role in the network's structure.

    In temporal networks, brokering centrality considers the temporal-delayed clustering
    coefficient [10]_, calculated with
    :func:`~networkx_temporal.algorithms.clustering_coefficient`. This behavior can be overriden
    by passing a dictionary ``clustering_coef`` with the defined values for each node.

    .. [9] Cai, J.J., Borenstein, E., Petrov, D.A. (2010).
           Broker Genes in Human Disease.
           Genome Biology and Evolution, 2.
           doi: `10.1093/gbe/evq064 <https://doi.org/10.1093/gbe/evq064>`_.

    .. [10] Chen, B., Hou, G., Li, A. (2024).
            Temporal local clustering coefficient uncovers the hidden pattern in temporal networks.
            Phys. Rev. E., 109(6).
            doi: `10.1103/PhysRevE.109.064302 <https://doi.org/10.1103/PhysRevE.109.064302>`_.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param clustering_coef: Dictionary of precomputed clustering coefficient values. Optional.
    """
    degree_centrality = nx.degree_centrality(G)

    if not clustering_coef:
        clustering_coef = clustering_coefficient(G)

    return {
        node: degree_centrality[node] * clustering_coef[node]
        for node in G.nodes()
    }
