from typing import Any, Optional, Union

import numpy as np
from numpy import ndarray


def block_matrix(
    communities: int,
    p: Optional[float] = None,
    q: Optional[float] = None,
) -> ndarray:
    """
    Returns a block matrix, used in stochastic block models.
    """
    assert type(communities) == int and communities > 0,\
        "The parameter `communities` must be a positive integer."

    assert p is None or (type(p) == float and 0 <= p <= 1),\
        "The parameter `p` must be a float between 0 and 1."

    assert q is None or (type(q) == float and 0 <= q <= 1),\
        "The parameter `q` must be a float between 0 and 1."

    if p is None and q is None:
        p = q = 1/communities

    B = np.zeros((communities, communities))
    return B


def transition_matrix(
    communities: int,
    eta: Optional[float] = None,
) -> ndarray:
    """
    Returns a transition matrix, used in dynamic stochastic block models.
    """
    if eta is None:
        eta = 1/communities

    return


def degree_vector(
    nodes: int,
    min_degree: int,
    max_degree: int,
) -> ndarray:
    """
    Returns a node degree vector used in stochastic block models.

    :param nodes: Number of nodes in the network.
    :param min_degree: Minimum degree of nodes.
    :param max_degree: Maximum degree of nodes.
    """
    return


def community_vector(nodes: Union[list, ndarray]) -> ndarray:
    """
    Returns a node community vector, used in stochastic block models.

    :param nodes: Number of nodes in each community.
    """
    return [i*[n] for i, n in enumerate(nodes)]
