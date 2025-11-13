from typing import List, Optional, Union

import numpy as np
from scipy.sparse import csr_matrix


def generate_block_matrix(
    k: int,
    p: Optional[float] = None,
    q: Optional[float] = None,
    sparse: Optional[bool] = False,
) -> np.ndarray:
    """ Generates a block matrix.

    A square matrix of size :math:`k \\times k` is generated where diagonal elements of the block
    matrix represent the probabilities of edges between nodes in the same community, while
    off-diagonal elements represent the probabilities of edges between nodes in different
    communities, i.e.,

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
            q & \\text{otherwise}.
        \\end{cases}

    In this function, parameters ``p`` and ``q`` are used to set the diagonal and off-diagonal
    elements, respectively. If both are unset, probabilities are uniformly distributed, i.e.,
    :math:`p = q = 1 / k`. If only one is unset, the other is set to
    :math:`p = 1 - q \\, (k - 1)` or :math:`q = (1 - p) / (k - 1)`, respectively.

    :param communities: Number of communities in the network.
    :param p: Edge probability among nodes in the same community.
    :param q: Edge probability among nodes in different communities.
    :param sparse: Returns a CSR matrix if ``True``. Default is ``False``.
    """
    if not (type(k) == int and k > 1):
        raise ValueError("Communities `k` must be an integer larger than 1.")
    if type(p) == float and not 0 <= p <= 1:
        raise ValueError("Diagonal `p` must be a float or list of floats between 0 and 1.")
    if type(q) == float and not 0 <= q <= 1:
        raise ValueError("Off-diagonal `q` must be a float or list of floats between 0 and 1.")

    if type(p) == list:
        if len(p) != k:
            raise ValueError("If `p` is a list, its length must match number of communities `k`.")
        p = np.array(p)
    if type(q) == list:
        if len(q) != k:
            raise ValueError("If `q` is a list, its length must match number of communities `k`.")
        q = np.array(q)

    if p is None and q is None:
        p = q = 1 / k
    elif p is None:
        p = 1 - (q * (k - 1))
    elif q is None:
        q = (1 - p) / (k - 1)

    B = np.eye(k, k) * p + (np.ones((k, k)) - np.eye(k, k)) * q

    if sparse:
        return csr_matrix(B)
    return B


def generate_transition_matrix(
    k: int,
    eta: Optional[Union[float, List[float]]] = None,
    uniform_all: Optional[bool] = False,
    sparse: Optional[bool] = False,
) -> np.ndarray:
    """ Generates a transition matrix.

    The transition matrix is a square and symmetrical matrix of size :math:`k \\times k` that
    describes the probabilities of nodes transitioning communities. The probability of a node
    remaining in its community is given by :math:`\\eta` = ``eta``, and that of transitioning
    to another community by :math:`1 - \\eta`, i.e.,

    .. math::

        \\boldsymbol{\\tau} =
        \\begin{pmatrix}
        \\tau_{11} & \\tau_{12} & \\cdots & \\tau_{1k} \\\\
        \\tau_{21} & \\tau_{22} & \\cdots & \\tau_{2k} \\\\
        \\vdots & \\vdots & \\ddots & \\vdots \\\\
        \\tau_{k1} & \\tau_{k2} & \\cdots & \\tau_{kk}
        \\end{pmatrix},\\,
        \\tau_{ij} =
        \\begin{cases}
            \\eta & \\text{if} \\, i = j \\\\
            \\frac{1 - \\eta}{k - 1} & \\text{otherwise},
        \\end{cases}

    where
    :math:`\\boldsymbol{\\tau}` is the transition matrix,
    :math:`\\eta \\in [0, 1]` is a parameter,
    and :math:`k` is the number of communities,
    so larger values of :math:`\\eta` increase the probability of nodes remaining in their current
    community.

    If ``eta`` is unset, it defaults to :math:`\\eta = 1/k`. A list of probabilities may also be
    provided to define non-uniform transition probabilities for each community, e.g.,
    ``eta = [0.8, 0.6, 0.9]`` for ``k=3``.

    .. note::

        If ``uniform_all=True``, uniform-at-random probabilities follow the original paper [1]_
        and include the node's current community in the distribution, i.e.,
        :math:`\\tau_{ij} = (1 - \\eta)/k + \\eta \\, \\delta(i,j)`,
        so nodes always have a non-zero probability of remaining in their current community.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> # Generate a transition matrix for 3 communities with varying stability rates:
        >>> tau = tx.generators.generate_transition_matrix(k=3, eta=[.5, .6, .8])
        >>> print(tau)

        array([[0.5, 0.25, 0.25],
               [0.2, 0.6 , 0.2 ],
               [0.1, 0.1,  0.8 ]])

    :param k: Number of communities in the network.
    :param eta: Probability of nodes remaining in their current community. Accepts a float
        or a list of floats of size :math:`k`.
    :param uniform_all: If ``True``, nodes remain in their current communities with
        an added probability :math:`(1 - \\eta)/k`. Default is ``False``.
    :param sparse: Returns a CSR matrix if ``True``. Default is ``False``.
    """
    if eta is None:
        eta = 1 / k

    off_diagonal = (1 - eta) / (k - 1)

    if uniform_all:
        uniform = (1 - eta) / k
        eta += uniform
        off_diagonal -= uniform / (k-1)

    tau = generate_block_matrix(k, p=eta, q=off_diagonal)

    if sparse:
        return csr_matrix(tau)
    return tau


def generate_community_vector(
    nodes: Union[int, list] = None,
    communities: Optional[int] = None,
    shuffle: Optional[bool] = False,
) -> list:
    """ Generates a node community vector.

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

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> # Generate a community vector for 10 nodes for each of 2 communities.
        >>> z = tx.generators.generate_community_vector(nodes=10, communities=2, shuffle=True)
        >>> print(z)

        [1 1 0 1 0 0 0 1 0 0 1 0 0 0 1 1 1 1 1 0]

    .. code-block:: python

        >>> # Generate a community vector for communities of different sizes.
        >>> z = tx.generators.generate_community_vector(nodes=[4, 6, 10], shuffle=False)
        >>> print(z)

        [0 0 0 0 1 1 1 1 1 1 2 2 2 2 2 2 2 2 2 2]

    :param nodes: An ``int`` with the number of nodes per community
        or a ``list`` with the number of nodes in each community (their sizes).
    :param communities: Number of communities, if ``nodes`` is an ``int``.
    :param shuffle: If ``True``, vector elements are shuffled. Optional.
    """
    if not (type(nodes) in (int, list)):
        raise ValueError("Argument `nodes` expects a positive integer or a list of integers.")
    if not ((type(nodes) == int and nodes > 0) or (type(nodes) == list and len(nodes) > 0)):
        raise ValueError("Argument `nodes` expects a positive integer or a list of integers.")
    if type(nodes) == list and not all(type(c) == int and c >= 0 for c in nodes):
        raise ValueError("Argument `nodes` must be a list of zero or positive integers.")
    if communities is not None and not (type(communities) == int and communities > 0):
        raise ValueError("Argument `communities` must be a positive integer.")
    if shuffle is not None and not (type(shuffle) == bool):
        raise ValueError("Argument `shuffle` must be a boolean.")

    community_vector = np.array(
        [_ for _ in [[c]*nodes for c in range(communities)] for _ in _]
        if type(nodes) == int else
        [_ for _ in [[i]*c for i, c in enumerate(nodes)] for _ in _]
    )

    if shuffle:
        np.random.shuffle(community_vector)
    else:
        community_vector = np.sort(community_vector)

    return list(community_vector)


def generate_degree_vector(
    nodes: Union[int, list],
    min_degree: Optional[int] = None,
    max_degree: Optional[int] = None,
    alpha: Optional[float] = None,
    phi: Optional[float] = None,
    shuffle: Optional[bool] = True,
    seed: Optional[int] = None,
) -> list:
    """ Generates a node degree vector.

    The degree vector is a list of integers with the degrees of each node in the graph, which may
    be provided to the :func:`~networkx_temporal.generators.dynamic_sbm` generator to create
    graphs with expected degree distributions.

    By default, if ``alpha`` and ``phi`` are unset, degrees are generated by sampling from a uniform
    distribution between :math:`d_{min}` and :math:`d_{max}`, that is,
    :math:`\\mathbf{d} = \\big[ d_{1}, d_{2}, \\cdots, d_{n} \\, | \\, d_{min} \\leq d \\leq d_{max} \\big]`.

    .. rubric:: Gaussian distribution

    If ``phi`` is set, the degree vector is sampled from a Gaussian (normal) distribution:

    .. math::

        \\mathbf{d} = \\big[
        d_{1}, \\cdots, d_{n} \\,| \\, d \\sim
        \\mathcal{N} \\big( \\mu = \\frac{d_{min} + d_{max}}{2}, \\,
        \\sigma = \\frac{d_{max} - d_{min}}{\\varphi} \\big), \\,
        d_{min} \\leq d \\leq d_{max}
        \\big],

    where :math:`\\varphi \\gt 0` is a standard deviation factor that controls how it is spread
    around the mean :math:`\\mu`.

    .. rubric:: Zipf distribution

    If ``alpha`` is set, the degree vector is sampled from a Zipf (power-law)
    distribution:

    .. math::

        \\mathbf{d} = \\big[
        d_{1}, \\cdots, d_{n} \\, | \\,
        p(d) = \\frac{d^{-(\\alpha + 1)}}{\\sum_{d_{min}}^{d_{max}} d^{-(\\alpha + 1)}}, \\,
        d_{min} \\leq d \\leq d_{max}
        \\big],\\\\

    where :math:`\\alpha \\gt 1` is the exponent of the power-law distribution that controls how
    heavy-tailed it is.

    .. rubric:: Example

    Comparison of degree distributions generated with this function:

    .. code-block:: python

        >>> import matplotlib.pyplot as plt
        >>> import networkx_temporal as tx
        >>>
        >>> d1 = tx.generators.generate_degree_vector(100, max_degree=20, seed=0)
        >>> d2 = tx.generators.generate_degree_vector(100, max_degree=20, phi=6, seed=0)
        >>> d3 = tx.generators.generate_degree_vector(100, max_degree=20, alpha=2, seed=0)
        >>>
        >>> fig = plt.figure(figsize=(6, 4))
        >>> plt.hist(d1, bins=20, alpha=0.5, label='Uniform distribution')
        >>> plt.hist(d2, bins=20, alpha=0.5, label='Gaussian (normal) $\\phi=6$')
        >>> plt.hist(d3, bins=20, alpha=0.5, label='Zipf (power-law) $\\alpha=2$')
        >>> plt.title("Node degree distributions ($n=100, deg_{max}=20$)")
        >>> plt.grid("#dddddd", linestyle='--', linewidth=0.5)
        >>> plt.legend()
        >>> plt.show()

    .. image:: ../../assets/figure/generators/generate_degree_vector.png
       :align: center

    :param nodes: An ``int`` with the number of nodes in the network
        or a ``list`` with the number of nodes in each community (their sizes)..
    :param min_degree: Minimum node degree. Defaults to ``1``.
    :param max_degree: Maximum node degree. Defaults to ``nodes - 1``.
    :param alpha: Exponent of the power-law degree distribution.
    :param phi: Standard deviation factor of the normal distribution.
    :param shuffle: If ``True``, vector elements are shuffled. Default.
    :param seed: Random seed for reproducibility. Optional.
    """
    if type(nodes) == int:
        nodes = [nodes]

    if not (type(nodes) in (int, list)):
        raise ValueError("Argument `nodes` expects a positive integer or a list of integers.")
    if min_degree is not None and min_degree < 0:
        raise ValueError("Argument `min_degree` must be a non-negative value.")
    if max_degree is not None and max_degree < (min_degree or 0):
        raise ValueError("Argument `max_degree` must be a non-negative value >= `min_degree`.")
    if alpha and phi:
        raise ValueError("Arguments `alpha` and `phi` are mutually exclusive.")
    if alpha is not None and alpha <= 0:
        raise ValueError("Argument `alpha` must be a positive integer or float.")
    if shuffle is not None and not (type(shuffle) == bool):
        raise ValueError("Argument `shuffle` must be a boolean.")
    if seed is not None and not (type(seed) == int):
        raise ValueError("Argument `seed` must be an integer.")

    degree_vector = np.zeros(sum(nodes), dtype=int)
    min_degree = 1 if min_degree is None else min_degree
    max_degree = (sum(nodes) - 1) if max_degree is None else max_degree

    indx = 0
    for i, num in enumerate(nodes):
        if seed is not None:
            np.random.seed(seed + i)
        if alpha:
            # Sample from a power-law (Zipf) distribution.
            d = np.random.zipf(alpha, num)
            d = np.clip(d, min_degree, max_degree)
            d = np.array(d, dtype=int)
        elif phi:
            # Sample from a normal distribution.
            mean = (min_degree + max_degree) / 2
            std_dev = (max_degree - min_degree) / phi
            d = np.random.normal(mean, std_dev, num)
            d = np.clip(d, min_degree, max_degree).astype(int)
        else:
            # Sample from a uniform distribution.
            d = np.array([np.random.randint(min_degree, max_degree + 1) for _ in range(num)])

        # Degree vectors do not return sorted.
        if shuffle is False:
            d = np.sort(d)

        degree_vector[indx:indx+num] = d
        indx += num

    return list(degree_vector)


def transition_node_memberships(
    community_vector: List[int],
    transition_matrix: List[float],
    snapshots: Optional[int] = None,
    seed: Optional[int] = None,
) -> np.ndarray:
    """ Simulates node-level community transitions.

    The function simulates the transition of nodes between communities at time :math:`t+1`
    based on a :math:`k \\times k` transition matrix :math:`\\boldsymbol{\\tau}`, where diagonals
    describe the probability of a node remaining in its current community and off-diagonals
    the probabilities of nodes switching to other communities.

    :param community_vector: List of integer node classes at time :math:`t`.
    :param transition_matrix: Square matrix of transition probabilities.
    :param snapshots: Number of time snapshots to simulate. If set, returns
        a list of community vectors for each time snapshot. Optional.
    :param seed: Random seed for reproducibility. Optional.
    """
    community_vector = np.array(community_vector, dtype=int)
    transition_matrix = np.array(transition_matrix, dtype=float)

    num_vertices = len(community_vector)
    num_clusters = len(set(community_vector))
    set_clusters = list(range(num_clusters))

    if transition_matrix.shape != (num_clusters, num_clusters):
        raise ValueError(
            "Transition matrix size must match the number of communities "
            f"({num_clusters} x {num_clusters})."
        )
    if not np.all(np.isclose(np.sum(transition_matrix, axis=1), 1.0)):
        raise ValueError("Transition matrix must be a stochastic matrix (rows sum to 1).")

    temporal_memberships = []

    for t in range(snapshots or 1):
        if seed is not None:
            np.random.seed(seed + t)
        new_memberships = np.array([
            np.random.choice(set_clusters, p=transition_matrix[community_vector[i]])
            for i in range(num_vertices)
        ])
        temporal_memberships.append(new_memberships)

    return np.array(temporal_memberships if snapshots else new_memberships)
