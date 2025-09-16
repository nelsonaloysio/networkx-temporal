from typing import Optional, Union

import numpy as np


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
            q & \\text{otherwise},
        \\end{cases}

    where :math:`\\mathbf{B}` is the block matrix,
    :math:`b_{ij}` governs edges between nodes in communities :math:`i` and :math:`j`,
    and :math:`k` is the number of ``communities``.
    The parameters ``p`` and ``q`` control the probabilities of edges between nodes in the
    same community and in different communities, respectively.
    Note that if both ``p`` and ``q`` are unset, probabilities are uniformly distributed, i.e.,
    :math:`p = q = 1 / k`. If only one of them is unset, the other is set to
    :math:`p = 1 - q \\, (k - 1)` or :math:`q = (1 - p) / (k - 1)`, respectively.

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
        p = q = 1 / communities
    if p is None:
        p = 1 - (q * (communities - 1))
    if q is None:
        q = (1 - p) / (communities - 1)

    # Commented as NetworkX's implementation takes densities instead of probabilities
    # in the block matrix received by the `stochastic_block_model` function.
    # assert p + q == 1, "The sum of `p` and `q` must be equal to 1."

    B = np.zeros((communities, communities))
    for i in range(communities):
        for j in range(communities):
            B[i, j] = p if i == j else q
    return B


def generate_transition_matrix(
    communities: int,
    eta: Optional[float] = None,
    uniform_all: Optional[bool] = False,
) -> np.ndarray:
    """
    Returns a transition matrix.

    The transition matrix is here defined as a square and symmetrical matrix of size :math:`k \\times k` that
    describes uniform probabilities for nodes transitioning communities. The probability of a node
    remaining in its community is given by :math:`\\eta` = ``eta``, and that of transitioning
    community by :math:`(1 - \\eta)`,

    .. math::

        \\boldsymbol{\\tau} =
        \\eta \\, \\mathbf{I} + (1 - \\eta) \\, \\frac{\\mathbf{J}-\\mathbf{I}}{k-1},

    where
    :math:`\\boldsymbol{\\tau}` is the transition matrix,
    :math:`\\eta \\in [0, 1]` is the transition probability,
    :math:`\\mathbf{I}` is the identity matrix,
    :math:`\\mathbf{J}` is a matrix of ones,
    and :math:`k` is the number of communities.
    Larger values of :math:`\\eta` increase the likelihood of nodes remaining in their communities,
    resulting in less complex dynamics.

    .. note::

        If ``uniform_all=True``, uniform-at-random probabilities follow the original paper [1]_
        and include the probability of a node remaining in its current community, i.e.,
        :math:`\\tau_{ii} = \\eta + (1 - \\eta)/k`.

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


def transition_node_memberships(
    community_vector: Union[list, np.ndarray],
    transition_matrix: Union[list, np.ndarray],
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Simulates node-level community transitions.

    The function simulates the transition of nodes between communities at time :math:`t+1`
    based on a transition matrix. Each node's new community is chosen according to the
    probabilities defined in the transition matrix, as well as by the node's
    current community membership.

    :param community_vector: List of integer node classes at time :math:`t`.
    :param transition_matrix: Square matrix of transition probabilities.
    :param seed: Random seed for reproducibility. Optional.
    """
    if type(community_vector) not in (list, np.ndarray):
        raise TypeError("`community_vector` must be a list or numpy array")
    if type(transition_matrix) not in (list, np.ndarray):
        raise TypeError("`transition_matrix` must be a list or numpy array")

    community_vector = np.array(community_vector, dtype=int)
    transition_matrix = np.array(transition_matrix, dtype=float)

    num_vertices = len(community_vector)
    num_clusters = len(set(community_vector))
    set_clusters = list(range(num_clusters))

    assert transition_matrix.shape[0] == transition_matrix.shape[1] == num_clusters,\
        "`transition_matrix` must be a squared matrix with size equal to the number of communities"
    assert np.all(np.isclose(np.sum(transition_matrix, axis=1), 1.0)),\
        "`transition_matrix` must be a stochastic matrix (rows sum to 1)"

    if seed is not None:
        np.random.seed(seed)

    new_memberships = np.array([
        np.random.choice(set_clusters, p=transition_matrix[community_vector[i]])
        for i in range(num_vertices)
    ])

    return new_memberships
