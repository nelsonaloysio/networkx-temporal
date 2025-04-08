from typing import Optional, Union

import networkx as nx
import numpy as np

from ...transform import from_snapshots
from ...typing import TemporalGraph, StaticGraph


def sbm_dynamic(
    block_matrix: Union[list, np.ndarray],
    degree_vector: Union[list, np.ndarray],
    community_vector: Union[list, np.ndarray],
    transition_matrix: Optional[Union[list, np.ndarray]] = None,
    snapshots: Optional[int] = 1,
    selfloops: Optional[bool] = False,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    create_using: Optional[StaticGraph] = None,
    keep_transition: Optional[bool] = False,
) -> TemporalGraph:
    """
    Returns a temporal graph using dynamic SBM.

    The dynamic Stochastic Block Model (SBM) [1]_ is a degree-corrected generative model for
    temporal network structures. It is a generalization of SBM that allows for the generation of networks
    with evolving community structures, where the probability of edges between nodes and their
    community memberships is fixed, but nodes may transition community over time.

    The model is defined by a block matrix :math:`\\mathbf{B}`, a transition matrix
    :math:`\\boldsymbol{\\tau}`, a node degree vector :math:`\\mathbf{d}`, and a node community
    vector :math:`\\mathbf{z}`, which are used to generate the network at each time step:

    .. math::
        \\mathbf{B} = \\begin{pmatrix}
        b_{11} & b_{12} & \\cdots & b_{1k} \\\\
        b_{21} & b_{22} & \\cdots & b_{2k} \\\\
        \\vdots & \\vdots & \\ddots & \\vdots \\\\
        b_{k1} & b_{k2} & \\cdots & b_{kk}
        \\end{pmatrix},
        \\,
        \\boldsymbol{\\tau} = \\begin{pmatrix}
        \\tau_{11} & \\tau_{12} & \\cdots & \\tau_{1k} \\\\
        \\tau_{21} & \\tau_{22} & \\cdots & \\tau_{2k} \\\\
        \\vdots & \\vdots & \\ddots & \\vdots \\\\
        \\tau_{k1} & \\tau_{k2} & \\cdots & \\tau_{kk}
        \\end{pmatrix},
        \\,
        \\mathbf{d} = \\begin{pmatrix}
        d_{1} \\\\
        d_{2} \\\\
        \\vdots \\\\
        d_{n}
        \\end{pmatrix},
        \\,
        \\mathbf{z} = \\begin{pmatrix}
        z_{1} \\\\
        z_{2} \\\\
        \\vdots \\\\
        z_{n}
        \\end{pmatrix},

    where :math:`k` is the number of communities
    and :math:`n` is the number of nodes in the network.

    At each time step, the model generates a network by sampling edges between nodes
    according to the block matrix :math:`\\mathbf{B}` and the transition matrix
    :math:`\\boldsymbol{\\tau}`. The degree vector :math:`\\mathbf{d}` is used to determine
    the number of edges for each node and is kept fixed across snapshots, while the community
    vector :math:`\\mathbf{z}` is used to determine the community membership of each node
    in the initial snapshot only.

    :param block_matrix: Block matrix used to generate the network.
    :param degree_vector: Degree vector used to generate the network.
    :param community_vector: Community vector used to generate the network.
    :param transition_matrix: Transition matrix used for snapshots.
        If ``None``, nodes do not transition communities over time.
    :param snapshots: Number of time steps to generate.
    :param selfloops: If ``True``, self-loops are allowed. Default is ``False``.
    :param directed: Whether edges are directed. Defaults to ``True``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param create_using: Graph constructor to use.
    :param keep_transition: If ``True``, node transition probabilities refer
        to its community in the previous snapshot. Default is ``False``.

    .. [1] A. Clauset, M. E. J. Newman, C. Moore (2016). ''Detectability Thresholds and Optimal
           Algorithms for Community Structure in Dynamic Networks''. Phys. Rev. X 6(3).
           doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevX.6.031005>`__.
    """
    assert snapshots is None or (type(snapshots) == int and snapshots > 0),\
        "The number of snapshots `t` must be a positive integer."
    assert type(block_matrix) in (list, np.ndarray),\
        "Argument `block_matrix` must be a list or numpy array."
    assert type(transition_matrix) in (None, list, np.ndarray),\
        "Argument `transition_matrix` must be a list or numpy array."
    assert type(degree_vector) in (list, np.ndarray),\
        "Argument `degree_vector` must be a list or numpy array."
    assert type(community_vector) in (list, np.ndarray),\
        "Argument `community_vector` must be a list or numpy array."
    assert len(degree_vector) == len(community_vector),\
        "The degree vector and community vector must have the same length."

    k = len(block_matrix)
    n = len(degree_vector)

    if create_using is None:
        create_using = getattr(nx, f"{'Di' if directed else ''}{'Multi' if multigraph else ''}Graph")
    if multigraph is None:
        multigraph = create_using().is_multigraph()
    if directed is None:
        directed = create_using().is_directed()

    graphs = []
    for t in range(snapshots):
        G = create_using()
        G.add_nodes_from(range(n))

        for i in range(n):
            di, zi = degree_vector[i], community_vector[i]

            if t > 0 and transition_matrix is not None:
                # Retrieve node community from previous snapshot.
                if keep_transition:
                    zi = graphs[-1].nodes[i]["community"]
                # Transition node among communities.
                zi = np.random.choice(k, p=transition_matrix[zi])

            G.add_node(i, community=zi)
            degree = 0

            while degree < di:

                # Sample a target community for the current node.
                zj = np.random.choice(k, p=block_matrix[zi])
                # List nodes from the target community.
                zj_nodes = np.where(community_vector == zj)[0]
                # Probabilities of edges between nodes in the target community.
                zj_probs = degree_vector[zj_nodes]/degree_vector[zj_nodes].sum()
                # Sample a target node from the target community.
                j = np.random.choice(zj_nodes, p=zj_probs)
                # Add an edge between the current node and the target node.
                if i != j or selfloops:
                    G.add_edge(i, j, time=t)
                    degree += (1 if directed else 2)

        graphs.append(G)

    return from_snapshots(graphs)


def generate_block_matrix(
    communities: int,
    p: Optional[float] = None,
    q: Optional[float] = None,
) -> np.ndarray:
    """
    Returns a block matrix.

    The block matrix is a square matrix of size :math:`k \\times k` that describes the
    probabilities of edges between nodes in different communities. The diagonal elements
    of the block matrix represent the probabilities of edges between nodes in the same
    community, while the off-diagonal elements represent the probabilities of edges
    between nodes in different communities, i.e.,

    .. math::

        \\mathbf{B} = \\begin{pmatrix}
        b_{11} & b_{12} & \\cdots & b_{1k} \\\\
        b_{21} & b_{22} & \\cdots & b_{2k} \\\\
        \\vdots & \\vdots & \\ddots & \\vdots \\\\
        b_{k1} & b_{k2} & \\cdots & b_{kk}
        \\end{pmatrix},\\,
        b_{ij} =
        \\begin{cases}
            p & \\text{if} \\, i = j \\\\
            q / k-1 & \\text{otherwise},
        \\end{cases}

    where :math:`\\mathbf{B}` is the block matrix,
    :math:`b_{ij}` is the probability of an edge between nodes in communities :math:`i` and :math:`j`,
    and :math:`k` is the number of ``communities``.
    The parameters ``p`` and ``q`` control the probabilities of edges between nodes in the
    same community and in different communities, respectively.

    :param communities: Number of communities in the network.
    :param p: Edge probability among nodes in the same community.
    :param q: Edge probability among nodes in different communities.
    """
    assert type(communities) == int and communities > 1,\
        "Argument `communities` must be an integer larger than 1."
    assert p is None or (type(p) == float and 0 <= p <= 1),\
        "Argument `p` must be a float between 0 and 1."
    assert q is None or (type(q) == float and 0 <= q <= 1),\
        "Argument `q` must be a float between 0 and 1."

    if p is None and q is None:
        p = (1 - (q or 0)) / communities
    if p is None:
        p = (1 - (q or 0))
    if q is None:
        q = (1 - p)

    assert p + q == 1, "The sum of `p` and `q` must be equal to 1."

    B = np.zeros((communities, communities))
    for i in range(communities):
        for j in range(communities):
            B[i, j] = p if i == j else (q/(communities - 1))
    return B


def generate_transition_matrix(
    communities: int,
    eta: Optional[float] = None,
    uniform_all: Optional[bool] = False,
) -> np.ndarray:
    """
    Returns a transition matrix.

    The transition matrix is a square and symmetrical matrix of size :math:`k \\times k` that
    describes the probabilities of nodes transitioning communities. The probability of a node
    remaining in its community is given by :math:`\\eta` = ``eta``, and that of transitioning
    community by :math:`(1 - \\eta)`, i.e.,

    .. math::

        \\boldsymbol{\\tau} =
        \\eta \\, \\mathbf{I} + (1 - \\eta) \\, \\frac{\\mathbf{J}-\\mathbf{I}}{k-1},

    where
    :math:`\\boldsymbol{\\tau}` is the transition matrix,
    :math:`\\eta \\in \\{0, 1\\}` is the transition probability,
    :math:`\\mathbf{I}` is the identity matrix,
    :math:`\\mathbf{J}` is a matrix of ones,
    and :math:`k` is the number of communities.
    Larger values of :math:`\\eta` increase the likelihood of nodes remaining in their communities,
    resulting in less complex dynamics.

    .. note::

        If ``uniform_all=True``, uniform-at-random probabilities follow the original paper [1]_
        and include the probability of remaining in the same community, i.e.,
        :math:`\\tau_{ij} = \\eta + (1 - \\eta)/k \\iff i=j`.

    :param communities: Number of communities in the network.
    :param eta: Probability of remaining in the same community.
    :param uniform_all: If ``True``, nodes remain in their current communities with
        a probability :math:`\\eta + (1 - \\eta)/k`. Default is ``False``.
    """
    eta = 1/communities if eta is None else eta

    assert type(eta) in (int, float) and 0 <= eta <= 1,\
        "Argument `eta` must be a float or integer between 0 and 1."

    if uniform_all:
        eta += ((1-eta)/communities)

    T = np.zeros((communities, communities))
    for i in range(communities):
        for j in range(communities):
            if i == j:
                T[i, j] = eta
            else:
                T[i, j] = (1-eta) / (communities - 1)
    return T


def generate_degree_vector(
    nodes: Union[int, list],
    min_degree: int,
    max_degree: int,
    alpha: Optional[float] = None,
    shuffle: bool = True,
) -> np.ndarray:
    """
    Returns a node degree vector.

    The degree vector is a list of integers with the degrees
    of each node in the graph and is used by degree-corrected SBMs.
    It is optionally generated by sampling from a power-law distribution,

    .. math::

        \\mathbf{d} = \\big[
        d_{1}, d_{2}, \\cdots, d_{n} \\, | \\,
        p(d) = \\frac{d^{-(\\alpha + 1)}}{\\sum_{d_{min}}^{d_{max}} d^{-(\\alpha + 1)}}, \\,
        d \\in \\{d_{min}, d_{max}\\}
        \\big],\\\\

    where
    :math:`p(d)` is the probability of a node having degree :math:`d`,
    :math:`n` is the number of nodes in the graph,
    :math:`d_{min}` and :math:`d_{max}` are the minimum and maximum degrees of the nodes,
    and :math:`\\alpha \\gt 1` is the exponent of the power-law distribution, which controls the
    steepness of the (Zipf) distribution.

    .. note ::

        If ``alpha`` is unset, the degree vector is generated by sampling from a uniform distribution
        between :math:`d_{min}` and :math:`d_{max}` instead, that is,
        :math:`\\mathbf{d} = \\big[ d_{1}, d_{2}, \\cdots, d_{n} \\, | \\, d_{min} \\leq d \\leq d_{max} \\big]`.

    :param nodes: An ``int`` with the number of nodes in the network
        or a ``list`` of the number of nodes in each community.
    :param min_degree: Minimum degree of nodes.
    :param max_degree: Maximum degree of nodes.
    :param alpha: Exponent of the power-law degree distribution.
    :param shuffle: If ``True``, the degree vector is shuffled. Default.
    """
    assert type(nodes) in (int, list),\
        "Argument `nodes` expects a positive integer or a list of integers."
    assert (type(nodes) == int and nodes > 0) or (type(nodes) == list and len(nodes) > 0),\
        "Argument `nodes` expects a positive integer or a list of integers."
    assert min_degree is None or type(min_degree) == int and min_degree >= 0,\
        "Argument `min_degree` must be a non-negative integer."
    assert max_degree is None or type(max_degree) == int and max_degree >= min_degree,\
        "Argument `max_degree` must be a non-negative integer >= `min_degree`."
    assert alpha is None or type(alpha) in (int, float) and alpha > 0,\
        "Argument `alpha` must be a positive integer or float."
    assert shuffle is None or type(shuffle) == bool,\
        "Argument `shuffle` must be a boolean."

    if type(nodes) == int:
        nodes = [nodes]

    degree_vector = np.zeros(sum(nodes), dtype=int)

    i = 0
    for num in nodes:
        if alpha:
            d = np.random.zipf(alpha, num)
            d = np.clip(d, min_degree, max_degree)
            d = np.array(d, dtype=int)
        else:
            d = np.array([np.random.randint(min_degree, max_degree + 1) for _ in range(num)])

        if shuffle is False:
            d = np.sort(d)

        degree_vector[i:i+num] = d
        i += num

    return degree_vector


def generate_community_vector(
    nodes: Union[int, list] = None,
    communities: Optional[int] = None,
    shuffle: bool = False,
) -> np.ndarray:
    """
    Returns a node community vector.

    The community vector is a list of integers that describes the community membership
    of each node in the graph and is used to generate the network at each time step.
    The community vector is generated by repeating the community index :math:`i` for
    each node in the community :math:`c`, i.e.,

    .. math::

        \\mathbf{z} = \\big[ z_{1}, z_{2}, \\cdots, z_{n} \\, | \\, z_{i} \\leq k \\big],

    where :math:`\\mathbf{z}` is the community vector,
    :math:`z_{i}` is the community index of node :math:`i`,
    :math:`c` is the community index,
    :math:`k` is the number of communities,
    and :math:`n` is the number of nodes in the network.

    :param nodes: An ``int`` with the number of nodes per community
        or a ``list`` of the number of nodes in each community.
    :param communities: Number of communities, if ``nodes`` is an ``int``.
    :param shuffle: If ``True``, the degree vector is shuffled. Optional.
    """
    assert type(nodes) in (int, list),\
        "Argument `nodes` expects a positive integer or a list of integers."
    assert (type(nodes) == int and nodes > 0) or (type(nodes) == list and len(nodes) > 0),\
        "Argument `nodes` expects a positive integer or a list of integers."
    assert type(nodes) != list or all(type(c) == int and c >= 0 for c in nodes),\
        "Argument `nodes` must be a list of zero or positive integers."
    assert type(communities) != int or communities > 0,\
        "Argument `communities` must be a positive integer."
    assert shuffle is None or type(shuffle) == bool,\
        "Argument `shuffle` must be a boolean."

    community_vector = np.array(
        [_ for _ in [[c]*nodes for c in range(communities)] for _ in _]
        if type(nodes) == int else
        [_ for _ in [[i]*c for i, c in enumerate(nodes)] for _ in _]
    )

    if shuffle:
        np.random.shuffle(community_vector)
    else:
        community_vector = np.sort(community_vector)

    return community_vector