from typing import List, Optional, Union

import numpy as np

from .modularity import _communities_list
from .modularity_spectral import spectral_modularity
from ...classes.types import is_temporal_graph
from ...typing import TemporalGraph, Literal


def longitudinal_modularity(
    TG: TemporalGraph,
    communities: Union[str, list, List[list]],
    resolution: Optional[float] = 1,
    smoothness: Optional[float] = 1,
    delta: Optional[float] = 1,
    membership_expectation: Literal["cm", "jm", "mm"] = "mm",
    weight: Optional[str] = "weight",
    sparse: bool = False,
) -> float:
    """ Returns the L-modularity of a temporal graph.

    Longitudinal modularity [6]_ is a generalization of the metric for temporal graphs, which adds
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

    .. [11] V. Brabant et al (2025). ''Longitudinal modularity, a modularity for
        link streams.'' EPJ Data Science, 14, 12. doi: `10.1140/epjds/s13688-025-00529-x
        <https://doi.org/10.1140/epjds/s13688-025-00529-x>`__.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param communities: List of community assignments for each node,
        or list of such lists for temporal community assignments. If a
        string, consider node attribute values with this key as community assignments.
    :param smoothness: The smoothness term :math:`\\omega`. Default is ``1``.
    :param resolution: The resolution parameter. Default is ``1``.
    :param delta: Minimum interval to consider for a node switch. Default is ``1``.
    :param membership_expectation: The membership expectation model to use.
        One of: ``'cm'`` (co-membership), ``'jm'`` (joint membership), or ``'mm'`` (mean
        membership). Default is ``'mm'``.
    :param weight: The edge attribute key used to compute edge weights. Default: ``'weight'``.
    """
    delta = 1 if delta is None else delta
    smoothness = 1 if smoothness is None else smoothness
    membership_expectation = "cm" if membership_expectation is None else membership_expectation

    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")

    n_nodes = TG.order(copies=False)

    communities = [
        _communities_list(G, communities[t] if type(communities[0]) == list else communities)
        for t, G in enumerate(TG)
    ]

    # k = len(set(communities[0]))
    # C = np.zeros((n_nodes, k))
    # for communities_vector in (communities if type(communities[0]) == list else [communities]):
    #     for i in range(n_nodes):
    #         C[i, communities_vector[i]] += 1 / len(communities)

    # theta, node_presence = longitudinal_link_expectation(
    #     TG, communities, membership_expectation
    # )
    return longitudinal_link_expectation(
        TG, communities, membership_expectation
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

    return float(Q)


def longitudinal_link_expectation(
    TG: TemporalGraph,
    communities: list,
    membership_expectation: Literal["cm", "jm", "mm"] = "mm",
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
    :param membership_expectation: The membership expectation model to use.
        One of: ``'cm'`` (co-membership), ``'jm'`` (joint membership), or ``'mm'`` (mean
        membership). Default is ``'mm'``.
    :param return_node_presence: Whether to also return the node presence lists.
    """
    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")
    if membership_expectation not in ("cm", "jm", "mm"):
        raise ValueError(
            "Membership expectation expects one of "
            "'cm' (co-membership), 'jm' (joint) or 'mm' (mean)."
        )

    communities = np.array(communities)
    timestamps = {n: set() for n in TG.temporal_nodes()}
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
    if membership_expectation == "cm":
        # theta = np.array([len(t) / total_time for t in node_presence])
        theta = np.zeros((n_nodes, total_time))
        for i, t in enumerate(unique_timestamps):
            for j, node in enumerate(node_presence):
                if t in node:
                    theta[j, i] = 1
        # theta = theta.sum(axis=1) / total_time
        return theta
    # Joint membership expectation.
    elif membership_expectation == "jm":
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
    elif membership_expectation == "mm":
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
