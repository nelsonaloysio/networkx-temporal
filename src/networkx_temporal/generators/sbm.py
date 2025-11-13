from typing import List, Optional

import networkx as nx
import numpy as np
import scipy.sparse as sp

from .generators import transition_node_memberships
from ..classes.factory import temporal_graph
from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import TemporalGraph, StaticGraph

try:
    from networkx import from_scipy_sparse_array
except ImportError:
    from networkx import from_scipy_sparse_matrix as from_scipy_sparse_array


def dynamic_stochastic_block_model(
    B: List[float],
    z: List[int],
    d: Optional[list[int]] = None,
    d_out: Optional[list[int]] = None,
    tau: Optional[list[float]] = None,
    fix_transition_prob: Optional[bool] = False,
    t: Optional[int] = 1,
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    selfloops: Optional[bool] = False,
    create_using: Optional[StaticGraph] = None,
    seed: Optional[int] = None,
    sparse: Optional[bool] = False,
) -> TemporalGraph:
    """ Generates a dynamic stochastic block model graph.
    Returns a :class:`~networkx_temporal.classes.TemporalGraph` object.

    This model is based on a dynamic SBM model [1]_, where nodes are assigned to communities
    that may transition over time, and edges are generated based on community memberships
    at each snapshot. Transitions are modeled as a Markov process, where the community
    membership of node :math:`i` at time :math:`t+1`, denoted by :math:`z^{(t+1)}_i`, depends
    only on its membership at time :math:`t`, i.e.,

    .. math::

        \\mathbb{P}(z^{(t+1)}_i) = \\tau_{z^{(t)}_i},

    where :math:`\\boldsymbol{\\tau}` is the transition matrix with the same shape of the
    block matrix :math:`\\mathbf{B}`. Adjacencies :math:`\\mathbf{A}^{(t)}` at snapshot :math:`t`
    are sampled from a Bernoulli distribution considering the temporal communities
    :math:`\\mathbf{z}^{(t)}`.

    If ``fix_transition_prob=True``, node community transition probabilities are fixed
    based on their initial memberships at :math:`t=0` for all :math:`t>0` snapshots; otherwise,
    considering their most recent memberships.
    For details on the generative model, see the
    :func:`~networkx_temporal.generators.stochastic_block_model` function.

    .. rubric:: Example

    To generate a dynamic SBM with :math:`k=4` communities of :math:`n=8` nodes each, :math:`p=0.8`
    within-community edge probabilities, :math:`t=4` snapshots, :math:`\\eta=0.9` temporal
    community stability, and expected node degree distribution following a Zipf (power-law)
    with exponent :math:`\\alpha=2`:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> n = 8       # Nodes per community.
        >>> k = 4       # Number of communities.
        >>> p = 0.8     # Within-community edge probability.
        >>> t = 4       # Number of snapshots.
        >>> eta = 0.9   # Stability of community memberships.
        >>> alpha = 2   # Exponent for degree distribution (Zipf).
        >>>
        >>> B = tx.generators.generate_block_matrix(k, p)
        >>> z = tx.generators.generate_community_vector(n, k)
        >>> d = tx.generators.generate_degree_vector([n]*k, max_degree=n, alpha=alpha, seed=0)
        >>> tau = tx.generators.generate_transition_matrix(k, eta)
        >>>
        >>> TG = tx.generators.dynamic_sbm(
        ...     B, z, d, tau=tau, t=t,
        ...     fix_transition_prob=False,
        ...     seed=0
        ... )
        >>> print(TG)

        TemporalMultiGraph (t=4) with 32 nodes and 184 edges

    Interaction times are stored in the edge attribute ``time``. To inspect how community sizes
    changed over time, we may iterate over snapshots and the node attribute ``community``:

    .. code-block:: python

        >>> community = [[c for n, c in G.nodes(data="community")] for G in TG]
        >>> for t, G in enumerate(TG):
        ...     clusters = [len([i for i in community[t] if i == c]) for c in set(community[t])]
        ...     print(f"t={t}: {G.order()} nodes, {G.size()} edges, {clusters} community sizes")

        t=0: MultiDiGraph with 60 nodes and 1453 edges, [30, 30] community sizes
        t=1: MultiDiGraph with 60 nodes and 1492 edges, [33, 27] community sizes

    Let's plot the resulting temporal graph, coloring nodes and edges by community memberships:

    .. code-block:: python

        >>> import matplotlib.pyplot as plt
        >>> colors = plt.cm.tab10.colors
        >>>
        >>> community = [[x for n, x in G.nodes(data="community")] for G in TG]
        >>>
        >>> node_color = [[colors[x] for n, x in G.nodes(data="community")] for G in TG]
        >>>
        >>> edge_color = [[colors[community[t][u]] if community[t][u] == community[t][v]
        >>>                else "gray" for u, v in G.edges()] for t, G in enumerate(TG)]
        >>>
        >>> tx.draw(TG,
        ...         figsize=(9, 2.5),
        ...         layout="circular",
        ...         temporal_node_color=node_color,
        ...         temporal_edge_color=edge_color,
        ...         node_size=120,
        ...         font_size=9)

    .. image:: ../../assets/figure/generators/dynamic_stochastic_block_model.png
       :align: center

    We observe that few nodes transition between communities over time as :math:`\\eta=0.9`, while
    most edges remain within communities and node degree distribution remains similar over time.

    .. [1] Amir Ghasemian et al. (2016).
        ''Detectability Thresholds and Optimal Algorithms for Community Structure in Dynamic
        Networks''. doi: `10.1103/PhysRevX.6.031005 <https://doi.org/10.1103/PhysRevX.6.031005>`__

    :param B: Block matrix with edge probabilities.
    :param z: Community vector assigning nodes to clusters.
    :param d: Vector of expected node degrees.
        For directed graphs, this sets the in-degree vector.
        If unset, no degree correction is applied.
    :param d_out: Degree vector with expected node out-degrees.
        For directed graphs, if unset, out-degrees are generated by permuting the in-degree vector.
        For undirected graphs, this parameter is ignored.
    :param tau: Transition matrix used for snapshots.
        If unset, nodes do not transition communities over time.
    :param t: Number of snapshots to generate.
    :param directed: Whether edges are directed. Defaults to ``False``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param selfloops: Allows self-loops. Defaults to ``False``.
    :param create_using: Graph constructor to use.
    :param fix_transition_prob: If ``True``, node transition probabilities refer
        to the ground truth probabilities in every snapshot. Default is ``False``.
    :param seed: Random number generator state.
    :param sparse: If ``True``, use sparse instead of dense matrices. Default is ``False``.

    :note: Alias to :func:`~networkx_temporal.generators.dynamic_sbm`.
    """
    if not (t is None or (type(t) == int and t > 0)):
        raise ValueError("Number of snapshots `t` must be a positive integer.")
    if len(B) != len(B[0]):
        raise ValueError("Block matrix `B` must be square.")
    if d is not None and (len(z) != len(d) or (d_out is not None and len(d) != len(d_out))):
        raise ValueError("Length of community vector `z` differs from degree vectors `d` or `d_out`.")
    if tau is not None and (len(tau) != len(B) or len(tau[0]) != len(B[0])):
        raise ValueError("Transition matrix `tau` must match block matrix `B` shpae.")
    if not (create_using is None or is_static_graph(create_using) or is_temporal_graph(create_using)):
        raise TypeError("Expected a static or temporal graph object for `create_using`.")
    if not (create_using is None or (multigraph is None and directed is None)):
        raise ValueError("Parameters `multigraph` and `directed` are exclusive with `create_using`.")

    n_nodes = len(z)
    degree_vector = d
    community_vector = z

    # Defaults to undirected if d_out is unset.
    if directed is None:
        directed = (
            (True if d_out is not None else False)
            if create_using is None
            else create_using.is_directed()
        )
    # Defaults to multigraph if unset.
    if multigraph is None:
        multigraph = (
            True if create_using is None else create_using.is_multigraph()
        )
    # Static graph constructor.
    create_using = getattr(
        nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph"
    )

    # Node in- and out-degree vectors.
    if d is not None:
        if directed:
            d_in = degree_vector
            if d_out is None:
                d_in = d_in / 2
                d_out = np.random.permutation(d_in)
        else:
            d_in = d_out = degree_vector
        theta_in = d_in / np.sqrt(np.sum(d_in))
        theta_out = d_out / np.sqrt(np.sum(d_out))

    # Block matrix as compressed sparse matrix.
    if sparse and not sp.issparse(B):
        B = sp.csc_matrix(B)

    # Generate snapshots.
    TG = temporal_graph(t=0, directed=directed, multigraph=multigraph)

    for ti in range(t or 1):
        rng = np.random.default_rng(seed + ti if seed is not None else None)

        # Transition nodes to communities based on current or initial memberships.
        if ti > 0 and tau is not None:
            community_vector = transition_node_memberships(
                community_vector=z if ti == 1 or fix_transition_prob else last_memberships,
                transition_matrix=tau,
                seed=seed + ti if seed is not None else None
            )
            last_memberships = community_vector

        # Probability matrix for adjacencies.
        if sparse:
            # Community assignment matrix.
            C = sp.csr_matrix((np.ones(n_nodes), (np.arange(n_nodes), community_vector)))
            # We decompose the matrix multiplications Θ_out · C · B · C^T · Θ_in for efficiency.
            P = C.dot(B)
            P = P.dot(C.T)
            # Remove self-loops if specified.
            if not selfloops:
                P.setdiag(0)
            # Take upper triangle for undirected graphs.
            if not directed:
                P = sp.triu(P)
            # Sample edges from Bernoulli distribution.
            if d is not None:
                # Degree-correction factors.
                P = sp.diags(theta_out).dot(P)
                P = P.dot(sp.diags(theta_in))
                # Rescale the probability matrix to approximate expected degree sum.
                total_expected_edges = P.sum()
                total_target_edges = sum(d_in + d_out)
                scaling_factor = total_target_edges / total_expected_edges
                P.data = np.clip(P.data * scaling_factor, 0, 1)
            # Construct adjacency matrix.
            P = sp.csr_matrix(P)
            A = sp.csr_matrix((rng.binomial(1, P.data), P.indices, P.indptr), shape=P.shape)
            # Generate graph from adjacency matrix.
            G = from_scipy_sparse_array(A, parallel_edges=multigraph, create_using=create_using)
        else:
            # Community assignment matrix.
            C = np.zeros((n_nodes, len(B)))
            C[np.arange(n_nodes), community_vector] = 1
            # We decompose the matrix multiplications Θ_out · C · B · C^T · Θ_in for efficiency.
            P = np.dot(C, B)
            P = np.dot(P, C.T)
            # Remove self-loops if specified.
            if not selfloops:
                np.fill_diagonal(P, 0)
            # Take upper triangle for undirected graphs.
            if not directed:
                P = np.triu(P)
            # Sample edges from Bernoulli distribution.
            if d is not None:
                # Degree-correction factors.
                P = np.multiply(theta_out[:, None], P)
                P = np.multiply(P, theta_in[None, :])
                # Rescale the probability matrix to approximate expected degree sum.
                total_expected_edges = P.sum()
                total_target_edges = sum(d_in + d_out)
                scaling_factor = total_target_edges / total_expected_edges
                P.data = np.clip(P.data * scaling_factor, 0, 1).flatten()
            # Construct adjacency matrix.
            A = np.array(rng.binomial(1, P.flatten())).reshape(P.shape)
            # Generate graph from adjacency matrix.
            G  = nx.from_numpy_array(A, parallel_edges=multigraph, create_using=create_using)

        nx.set_node_attributes(G, {n: c for n, c in zip(G.nodes(), community_vector)}, "community")
        nx.set_edge_attributes(G, ti, "time")
        TG.append(G)

    return TG


def stochastic_block_model(
    B: List[float],
    z: List[int],
    d: Optional[list[int]] = None,
    d_out: Optional[list[int]] = None,
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    selfloops: Optional[bool] = False,
    create_using: Optional[StaticGraph] = None,
    seed: Optional[int] = None,
    sparse: Optional[bool] = False,
) -> StaticGraph:
    """ Generates a stochastic block model graph.
    Returns a :class:`~networkx_temporal.typing.StaticGraph` object.

    Adjacencies :math:`\\mathbf{A}` are sampled from a Bernoulli distribution given by
    probabilities computed by

    .. math::

        \\mathbb{P}(\\mathbf{A} \\vert \\mathbf{B}, \\mathbf{z}, \\mathbf{d}, \\mathbf{d_{out}}) =
        \\mathbf{\\Theta_{out}} \\; \\mathbf{C} \\; \\mathbf{B} \\;
        \\mathbf{C}^\\text{T} \\; \\mathbf{\\Theta_{in}},

    where :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix and
    :math:`\\mathbf{\\Theta}` are diagonal matrices of degree-correction factors given by the
    inverse square root of the sum of expected node degrees, i.e.,

    .. math::

        \\theta_{in,i} = \\frac{d_i}{\\sqrt{\\sum_{j=1}^{n} d_j}} \\quad \\text{and} \\quad
        \\theta_{out,i} = \\frac{d_{out,i}}{\\sqrt{\\sum_{j=1}^{n} d_{out,j}}}.

    If ``d_out=None``, out-degrees are generated by permuting the in-degree vector for directed
    graphs; for undirected graphs, the parameter is ignored so in-degrees are equal to out-degrees.

    .. seealso::

        For efficient generation of larger networks by stochastic block modeling,
        see the `graph-tool <https://graph-tool.skewed.de>`__
        library, which provides more efficient implementations of SBM models
        for static graphs.

    :param B: Block matrix with edge probabilities.
    :param z: Community vector assigning nodes to clusters.
    :param d: Vector of expected node degrees.
        For directed graphs, this sets the in-degree vector.
        If unset, no degree correction is applied.
    :param d_out: Degree vector with expected node out-degrees.
        For directed graphs, if unset, out-degrees are generated by permuting the in-degree vector.
        For undirected graphs, this parameter is ignored.
    :param tau: Transition matrix used for snapshots.
        If unset, nodes do not transition communities over time.
    :param t: Number of snapshots to generate.
    :param directed: Whether edges are directed. Defaults to ``False``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param selfloops: Allows self-loops. Defaults to ``False``.
    :param create_using: Graph constructor to use.
    :param fix_transition_prob: If ``True``, node transition probabilities refer
        to the ground truth probabilities in every snapshot. Default is ``False``.
    :param seed: Random number generator state.
    :param sparse: If ``True``, use sparse instead of dense matrices. Default is ``False``.
    """
    return dynamic_stochastic_block_model(
        B,
        z,
        d=d,
        d_out=d_out,
        tau=None,
        t=1,
        directed=directed,
        multigraph=multigraph,
        selfloops=selfloops,
        create_using=create_using,
        seed=seed,
        sparse=sparse,
    )[0]
