from typing import Optional, Union

import networkx as nx
import numpy as np

from .utils import transition_node_memberships
from ...transform import from_snapshots
from ...typing import TemporalGraph, StaticGraph


def stochastic_block_model(
    block_matrix: Union[list, np.ndarray],
    community_vector: Union[list, np.ndarray],
    transition_matrix: Optional[Union[list, np.ndarray]] = None,
    snapshots: Optional[int] = 1,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    selfloops: Optional[bool] = None,
    create_using: Optional[StaticGraph] = None,
    seed: Optional[int] = None,
    sparse: Optional[bool] = True,
    fix_transition_prob: Optional[bool] = False,
) -> TemporalGraph:
    """
    Returns a :class:`~networkx_temporal.classes.TemporalGraph`.
    Employs the Stochastic Block Model (SBM) available in NetworkX.

    This funtion allows for the generation of networks with dynamic community structures, where
    nodes can transition between communities over time.
    The underlying implementation relies on the
    `stochastic_block_model <https://networkx.org/documentation/stable/reference/generated/networkx.generators.community.stochastic_block_model.html>`__
    from NetworkX, where ``block_matrix`` defines the density of edges between nodes in
    different communities.
    Temporal dynamics are introduced based on a dynamic SBM [1]_ implementation where
    ``community_vector`` defines initial node memberships and ``transition_matrix`` defines the
    probability of nodes switching communities at each time step.

    .. [1] Amir Ghasemian et al. (2016).
       ''Detectability Thresholds and Optimal Algorithms for Community Structure in Dynamic Networks.''
       doi: `10.1103/PhysRevX.6.031005 <https://doi.org/10.1103/PhysRevX.6.031005>`__

    .. seealso::

        For efficient generation of larger networks and degree-corrected graphs,
        see the `graph-tool <https://graph-tool.skewed.de>`__
        library, which provides more efficient implementations of SBM models
        for static networks.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx

        >>> n = 1024   # Number of nodes.
        >>> k = 8      # Number of communities.
        >>> t = 8      # Number of time steps (snapshots).
        >>> eta = 0.9  # Community stability (0.0 < eta < 1.0).
        >>> p = 0.01   # Density of edges within communities.
        >>> q = 0.005  # Density of edges between communities.

        >>> block_matrix = tx.generators.generate_block_matrix(k, p=p, q=q)
        >>> transition_matrix = tx.generators.generate_transition_matrix(k, eta=eta)
        >>> community_vector = tx.generators.generate_community_vector(n, k)

        >>> TG = tx.generators.stochastic_block_model(
        ...     block_matrix,
        ...     community_vector,
        ...     transition_matrix,
        ...     snapshots=t,
        ... )

        >>> print(TG)

        TemporalGraph (t=8) with 8192 nodes and 503872 edges

    :param block_matrix: Block matrix, where elements give the density of
        edges between community pairs.
    :param community_vector: Community vector used to generate the network.
    :param transition_matrix: Transition matrix used for snapshots.
        If ``None``, nodes do not transition communities over time.
    :param snapshots: Number of time steps to generate.
    :param directed: Whether edges are directed. Defaults to ``True``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param selfloops: If ``True``, self-loops are allowed. Default is ``False``.
    :param create_using: Graph constructor to use.
    :param fix_transition_prob: If ``True``, node transition probabilities refer
        to the ground truth probabilities in every snapshot. Default is ``False``.
    :param seed: Random number generator state.
    :param sparse: Use the sparse heuristic to speed up the generator. Default is ``True``.
    """
    assert snapshots is None or (type(snapshots) == int and snapshots > 0),\
        "The number of snapshots `t` must be a positive integer."
    assert type(block_matrix) in (list, np.ndarray),\
        "Argument `block_matrix` must be a list or numpy array."
    assert type(transition_matrix) in (None, list, np.ndarray),\
        "Argument `transition_matrix` must be a list or numpy array."
    assert type(community_vector) in (list, np.ndarray),\
        "Argument `community_vector` must be a list or numpy array."
    # assert len(degree_vector) == len(community_vector),\
    #     "The degree vector and community vector must have the same length."

    k = len(block_matrix)
    n = len(community_vector)

    if create_using is None:
        create_using = getattr(nx, f"{'Di' if directed else ''}{'Multi' if multigraph else ''}Graph")
    if multigraph is None:
        multigraph = create_using().is_multigraph()
    if directed is None:
        directed = create_using().is_directed()

    graphs = []
    labels = community_vector

    for t in range(snapshots or 1):
        if t > 0 and transition_matrix is not None:
            labels = transition_node_memberships(
                community_vector if fix_transition_prob else labels,
                transition_matrix,
                seed=seed,
            )
        G = nx.stochastic_block_model(
            [len(labels[labels == i]) for i in range(k)],
            p=block_matrix,
            nodelist=list(range(n)),
            seed=seed,
            directed=directed,
            selfloops=selfloops,
            sparse=sparse,
        )
        nx.set_node_attributes(G, {node: label for node, label in zip(G.nodes(), labels)}, "label")
        graphs.append(G)

    return from_snapshots(graphs)


