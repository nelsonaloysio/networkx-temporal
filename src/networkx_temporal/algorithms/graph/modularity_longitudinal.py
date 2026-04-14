from typing import Optional, Union

import numpy as np

from .modularity import modularity
from ...classes import is_temporal_graph
from ...typing import TemporalGraph, Literal
from ...utils import map_attr_to_nodes


def longitudinal_modularity(
    TG: TemporalGraph,
    communities: Union[list, str, dict],
    resolution: Optional[float] = 1,
    smoothing: Optional[float] = 1,
    delta: Optional[float] = 1,
    expectation: Literal["cm", "jm", "mm"] = "mm",
    weight: Optional[str] = "weight",
    spectral: bool = False
) -> float:
    """ Returns the L-modularity of a temporal graph.

    Longitudinal modularity [11]_ is a generalization of the metric for temporal graphs, which adds
    a smoothness term to penalize nodes switching communities and the membership expectation
    for the lifetimes of pairs of nodes in the same community in a null model. It is defined as:

    .. math::

        Q_{\\textnormal{L}} =
        \\frac{1}{2m} \\sum_{C \\in \\mathcal{G}} \\left[ \\sum_{(i,j) \\in V^2}
        A_{ij} \\, \\delta(c_i, c_j)  - \\gamma \\frac{d_i^{out} \\, d_j^{in}}{2m}

        \\frac{\\sqrt{|T_{i \\in V_C}| |T_{j \\in V_C}|}}{|T|} \\right]
        - \\frac{\\omega}{2m} \\sum_{i \\in V} \\eta_i,

    where
    :math:`m` is the number of (undirected) edges in the graph,
    :math:`C \\in \\mathcal{G}` are all of its communities,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`d` are node degrees,
    :math:`T` is the set of all snapshots,
    :math:`\\omega = 1` (default) is a smoothing parameter,
    and :math:`\\eta` is the community switch count of a node,
    equivalent to the number of times it joins (or rejoins) a community minus one.

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

    Note that if ``spectral=True``, modularity is computed using
    :func:`~networkx_temporal.algorithms.spectral_modularity` instead.

    .. [11] V. Brabant et al (2025). ''Longitudinal modularity, a modularity for
        link streams.'' EPJ Data Science, 14, 12. doi: `10.1140/epjds/s13688-025-00529-x
        <https://doi.org/10.1140/epjds/s13688-025-00529-x>`__.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param communities: String (node attribute name), list of community assignments,
        or list of such lists (for temporal graphs).
    :param resolution: The resolution parameter. Defaults to ``1``.
    :param smoothing: Temporal smoothness parameter (default: ``1``).
    :param delta: Minimum interval to consider for a node switch. Default is ``1``.
    :param expectation: The membership presence expectation model to use.
        One of: ``'cm'`` (co-membership), ``'jm'`` (joint membership), or ``'mm'`` (mean
        membership). Default is ``'mm'``.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param spectral: Whether to use the spectral method to compute modularity.
        If ``False`` (default), use `NetworkX modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.
    """
    delta = 1 if delta is None else delta
    smoothing = 1 if smoothing is None else smoothing
    resolution = 1 if resolution is None else resolution
    expectation = "mm" if expectation is None else expectation

    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")

    Q = modularity(TG, communities, weight=weight, resolution=resolution, spectral=spectral)
    labels = map_attr_to_nodes(TG, communities)

    # Count node appearances over time.
    temporal_nodes = {}
    for G in TG:
        for node in G.nodes():
            temporal_nodes[node] = temporal_nodes.get(node, 0) + 1

    # Combine intra- and inter-slice modularity contributions.
    Q_l = (sum(Q) + (interslice_weight * within_interslice_edges)) / (2 * mu)

    n_nodes = TG.order(copies=False)

    communities = [
        _communities_list(G, communities[t] if type(communities[0]) == list else communities)
        for t, G in enumerate(TG)
    ]

    if spectral:
        k = len(set(communities[0]))
        C = np.zeros((n_nodes, k))
        for communities_vector in (communities if type(communities[0]) == list else [communities]):
            for i in range(n_nodes):
                C[i, communities_vector[i]] += 1 / len(communities)

        theta, node_presence = longitudinal_link_expectation(
            TG, communities, expectation=expectation, return_node_presence=True
        )

        unique_timestamps = set(_ for t in node_presence for _ in t)
        total_time = len(unique_timestamps)

        Q = spectral_modularity(TG.to_static(),
                                communities,
                                theta=theta,
                                weight=weight,
                                directed=TG.is_directed(),
                                resolution=resolution,
                                norm=total_time)

        # # Modularity matrix with longitudinal link expectation.
        # B = A - (((d_out*p).reshape(-1, 1) @ (d_in*p).reshape(1, -1) * resolution
        #          ) / ((C.T @ A @ C).sum() / total_time))

        # Compute modularity.
        s = smoothness_penalty(node_presence, delta)
        s = smoothness * s.sum() / sum(TG.size())
        Q -= s

    return Q_l



def longitudinal_link_expectation(
    TG: TemporalGraph,
    communities: list,
    expectation: Literal["cm", "jm", "mm"] = "mm",
    return_node_presence: bool = True,
) -> np.array:
    """ Calculates the link expectation vector for longitudinal modularity.

    Returns the vector :math:`\\theta` where each entry :math:`\\theta_i` is the
    membership expectation for node :math:`i` according to the selected model.

    Membership expectation models:

    - Co-membership (``'cm'``):
      :math:`\\theta_i = \\frac{|T_{i \\in V_C}|}{|T|}`, where
      :math:`|T_{i \\in V_C}|` is the number of timestamps where node :math:`i` appears in
      the same community as at least one other node, and :math:`|T|` is the total number of
      timestamps.
    - Joint membership (``'jm'``):
      :math:`\\theta_i = \\frac{|T_{C}|}{|T|}`, where :math:`|T_C|` is
      the number of timestamps where at least one node from community :math:`C` (of node :math:`i`)
      appears.
    - Mean membership (``'mm'``):
      :math:`\\theta_i = \\frac{\\sqrt{|T_{i \\in V_C}|}}{|T|}`, where
      :math:`|T_{i \\in V_C}|` is the number of timestamps where node :math:`i` appears in the same
      community as at least one other node, and :math:`|T|` is the total number of timestamps.

    If ``return_node_presence=True``, also returns a list of lists with the
    timestamps where each node appears.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param communities: List of community assignments for each node.
    :param expectation: The membership expectation model to use.
        One of: ``'cm'`` (co-membership), ``'jm'`` (joint membership), or ``'mm'`` (mean
        membership). Default is ``'mm'``.
    :param return_node_presence: Whether to also return the node presence lists.
    """
    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")
    if expectation not in ("cm", "jm", "mm"):
        raise ValueError(
            "Membership expectation expects one of "
            "'cm' (co-membership), 'jm' (joint) or 'mm' (mean)."
        )

    communities = np.array(communities)
    timestamps = {n: set() for n in TG.nodes(copies=False)}
    n_nodes = len(timestamps)

    # Longitudinal link expectation model.
    node_timestamps = [set() for _ in range(n_nodes)]
    for t, edgelist in enumerate(TG.edges()):
        for u, v in edgelist:
            node_timestamps[u].add(int(t))
            node_timestamps[v].add(int(t))

    node_presence = [sorted(list(t)) for t in node_timestamps]
    unique_timestamps = set(_ for t in node_presence for _ in t)
    total_time = len(unique_timestamps)

    # Co-membership expectation: θ_i = (d_u*d_v/2m) * (|T_{uv in C}|/|T|).
    if expectation == "cm":
        # theta = np.array([len(t) / total_time for t in node_presence])
        theta = np.zeros((n_nodes, total_time))
        for i, t in enumerate(unique_timestamps):
            for j, node in enumerate(node_presence):
                if t in node:
                    theta[j, i] = 1
        # theta = theta.sum(axis=1) / total_time
        return theta
    # Joint membership expectation.
    elif expectation == "jm":
        community_presence = {}
        if communities.ndim == 1:
            # Static community assignments.
            for u in range(len(communities)):
                if communities[u] not in community_presence:
                    community_presence[communities[u]] = set()
                community_presence[communities[u]].update(set(node_presence[u]))
            theta = np.array([
                len(community_presence[communities[u]]) / total_time
                for u in range(len(communities))
            ])
        else:
            # Dynamic community assignments.
            for t in range(len(communities)):
                for u in range(len(communities[t])):
                    if communities[t][u] not in community_presence:
                        community_presence[communities[t][u]] = set()
                    community_presence[communities[t][u]].update(set(node_presence[u]))
            theta = np.array([
                [len(community_presence[communities[t][u]]) / total_time
                 for u in range(len(communities[t]))]
                for t in range(len(communities))
            ])
        return theta

    # Mean membership expectation.
    elif expectation == "mm":
        if communities.ndim == 1:
            # Static community assignments.
            theta = np.array(
                [(len(t) ** 0.5) / total_time for t in node_presence])
        else:
            # Dynamic community assignments.
            theta = np.array([
                [(len(node_presence[u]) ** 0.5) / total_time
                 for u in range(len(communities[t]))]
                for t in range(len(communities))
            ])

    return (theta, node_presence) if return_node_presence else theta


def smoothness_penalty(node_presence: list, delta: float = 1) -> np.array:
    """ Calculates the smoothness vector for longitudinal modularity.

    :param presence_vector: List of lists with node presence timestamps.
    :param delta: Minimum time difference for node switches. Default is ``1``.
    """
    return  np.array([sum([1 for ti, tj in zip(node_presence[u][:-1], node_presence[u][1:])
                           if (tj-ti)>delta]) for u in range(len(node_presence))])
