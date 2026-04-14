from typing import List, Optional

import networkx as nx
import numpy as np
import scipy.sparse as sp

from ..generators import transition_node_memberships
from ...classes.factory import empty_graph
from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import TemporalGraph, StaticGraph

try:
    from networkx import from_scipy_sparse_array
except ImportError:
    from networkx import from_scipy_sparse_matrix as from_scipy_sparse_array


def dynamic_stochastic_block_model(
    B: List[List[float]],
    z: List[int],
    d: Optional[List[int]] = None,
    d_out: Optional[List[int]] = None,
    t: Optional[int] = 1,
    transition_matrix: Optional[List[float]] = None,
    fix_transition_prob: Optional[bool] = False,
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    isolates: Optional[bool] = True,
    selfloops: Optional[bool] = False,
    create_using: Optional[StaticGraph] = None,
    seed: Optional[int] = None,
    normal: Optional[bool] = True,
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

        \\mathbb{P}(z_i^{(t+1)}) = \\tau({z_i^{(t)}}),

    where :math:`\\boldsymbol{\\tau}` is the transition matrix with the same shape of the
    block matrix :math:`\\mathbf{B}`. Adjacencies :math:`\\mathbf{A}^{(t)}` at snapshot :math:`t`
    are sampled from a Poisson (default) or Bernoulli (if ``normal=False``) distribution
    considering the temporal communities :math:`\\mathbf{z}^{(t)}`.

    .. math::

        \\mathbb{P}(\\mathbf{A}^{(t)} \\vert \\mathbf{B}, \\mathbf{z}^{(t)}, \\mathbf{d}, \\mathbf{d_{out}}) =
        \\mathbf{\\Theta_{out}} \\; \\mathbf{C} \\; \\mathbf{B} \\;
        \\mathbf{C}^\\text{T} \\; \\mathbf{\\Theta_{in}},

    where :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix and
    :math:`\\mathbf{\\Theta}` are diagonal matrices of degree-correction factors given by the inverse square root of the sum of expected node degrees.
    Degree-correction factors are computed based on the expected degree vectors, which are
    fixed over time, and not based on the actual degree of nodes at each snapshot.

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
        >>> n = 8          # Nodes per community.
        >>> k = 4          # Number of communities.
        >>> t = 4          # Number of temporal snapshots.
        >>> p = 0.8        # Within-community edge probability.
        >>> eta = 0.9      # Stability of community memberships.
        >>> alpha = 2      # Exponent for degree distribution (Zipf).
        >>>
        >>> B = tx.generate_block_matrix(k, p)
        >>> z = tx.generate_community_vector(n, k)
        >>> d = tx.generate_degree_vector([n]*k, max_degree=n, alpha=alpha, seed=0)
        >>> tau = tx.generate_transition_matrix(k, eta)
        >>>
        >>> TG = tx.generators.dynamic_sbm(
        >>>     B=B, z=z, d=d, t=t,
        >>>     transition_matrix=tau,
        >>>     fix_transition_prob=False,
        >>>     seed=0
        >>> )
        >>> print(TG)

        TemporalMultiGraph (t=4) with 32 nodes and 184 edges

    Interaction times are stored in the edge attribute ``time``. To inspect how community sizes
    changed over time, we may iterate over snapshots and the node attribute ``community``:

    .. code-block:: python

        >>> community = tx.get_node_attributes(TG, "community")
        >>> for t, G in enumerate(TG):
        ...     clusters = [len([i for i in community[t] if i == c]) for c in set(community[t])]
        ...     print(f"t={t}: {G.order()} nodes, {G.size()} edges, {clusters} community sizes")

        t=0: MultiDiGraph with 60 nodes and 1453 edges, [30, 30] community sizes
        t=1: MultiDiGraph with 60 nodes and 1492 edges, [33, 27] community sizes

    Let's plot the resulting temporal graph, coloring nodes and edges by community memberships.
    We observe that few nodes transition between communities over time as :math:`\\eta=0.9`, while
    most edges remain within communities and node degree distribution remains similar over time:

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

    .. seealso::

        The `graph-tool <https://graph-tool.skewed.de>`__ library, which provides more efficient
        implementations of advanced models with features such as hierarchical community structures.
        For a model example with graph-tool for time-varying attributed graphs, see also:
        `tadc-sbm <https://github.com/nelsonaloysio/tadcsbm>`__.jkiodes

    .. [1] Amir Ghasemian et al. (2016).
        ''Detectability Thresholds and Optimal Algorithms for Community Structure in Dynamic
        Networks''. doi: `10.1103/PhysRevX.6.031005 <https://doi.org/10.1103/PhysRevX.6.031005>`__

    :param B: Block matrix with edge probabilities.
    :param z: Community vector assigning nodes to clusters.
    :param d: Vector of expected node degrees.
        For directed graphs, this sets the in-degree vector.
    :param d_out: Expected node out-degrees vector.
        For directed graphs, if unset, out-degrees are generated by permuting the in-degree vector.
        For undirected graphs, this parameter is ignored.
    :param t: Number of snapshots to generate.
    :param transition_matrix: Transition matrix used for snapshots.
        If unset, nodes do not transition communities over time.
    :param directed: Whether edges are directed. Defaults to ``False``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param isolates: Allows isolated nodes. Default is ``True``.
    :param selfloops: Allows self-loops. Default is ``False``.
    :param create_using: Graph constructor to use.
    :param fix_transition_prob: If ``True``, node transition probabilities refer
        to the ground truth probabilities in every snapshot. Default is ``False``.
    :param seed: Random number generator state.
    :param sparse: Whether to use sparse matrices. Default is ``False``.

    :note: Alias to :func:`~networkx_temporal.generators.dynamic_sbm`.
    """
    if not (t is None or (type(t) == int and t > 0)):
        raise ValueError("Number of snapshots `t` must be a positive integer.")
    if not (create_using is None or is_static_graph(create_using) or is_temporal_graph(create_using)):
        raise TypeError("Expected a static or temporal graph object for `create_using`.")
    if not (create_using is None or (multigraph is None and directed is None)):
        raise ValueError("Parameters `multigraph` and `directed` are exclusive with `create_using`.")

    # block_matrix = B
    if len(B) != len(B[0]):
        raise ValueError("Block matrix `B` must be square.")

    communities = z
    if len(z) < 1:
        raise ValueError("Community vector `z` must have at least one node.")
    if any(c < 0 or c >= len(B) for c in z):
        raise ValueError("Community vector `z` contains invalid community indices.")

    tau = transition_matrix
    if tau is not None and (len(tau) != len(B) or len(tau[0]) != len(B[0])):
        raise ValueError("Transition matrix `tau` must match block matrix `B` shape.")

    deg = d
    if d is not None and (len(z) != len(d) or (d_out is not None and len(d) != len(d_out))):
        raise ValueError("Communities `z` length differs from degree vectors `deg` or `deg_out`.")

    n_nodes = len(z)
    n_clusters = len(B)

    if directed is None:
        directed = (
            (True if d_out is not None else False)
            if create_using is None
            else create_using.is_directed()
        )

    if multigraph is None:
        multigraph = (
            True
            if create_using is None
            else create_using.is_multigraph()
        )

    # Static graph constructor.
    create_using = getattr(
        nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph"
    )

    # Node in- and out-degree vectors.
    if deg is not None:
        if directed:
            d_in = np.array(deg)
            if d_out is None:
                d_in = d_in / 2
                d_out = np.random.permutation(d_in)
        else:
            d_in = d_out = np.array(deg)
        theta_in = d_in / np.sqrt(np.sum(d_in))
        theta_out = d_out / np.sqrt(np.sum(d_out))

    # Block matrix as compressed sparse matrix.
    if sparse and not sp.issparse(B):
        B = sp.csc_matrix(B)

    # Generate snapshots.
    TG = empty_graph(directed=directed, multigraph=multigraph)

    for ti in range(t or 1):
        rng = np.random.default_rng(seed + ti if seed is not None else None)

        # Transition nodes to communities based on current or initial memberships.
        if ti > 0 and tau is not None:
            communities = transition_node_memberships(
                communities=z if fix_transition_prob else communities,
                transition_matrix=tau,
                seed=seed + ti if seed is not None else None
            )

        # Probability/Expectation matrix for adjacencies.
        if sparse:
            # Community assignment matrix.
            C = sp.csr_matrix((np.ones(n_nodes), (np.arange(n_nodes), communities)))
            # We decompose the matrix multiplications Θ_out · C · B · C^T · Θ_in for efficiency.
            P = C.dot(B)
            P = P.dot(C.T)
            # Remove self-loops if specified.
            if not selfloops:
                P.setdiag(0)
            # Take upper triangle for undirected graphs.
            if not directed:
                P = sp.triu(P)
            # Sample edges from distribution.
            if d is not None:
                # Degree-correction factors.
                P = sp.diags(theta_out).dot(P)
                P = P.dot(sp.diags(theta_in))
            # Scaling with clipping so probabilities are in [0, 1] if Bernoulli sampling.
            total_expected_edges = P.sum()
            total_target_edges = sum(d_in + d_out) if deg is not None else total_expected_edges
            scaling_factor = total_target_edges / total_expected_edges
            P = sp.csr_matrix(P)
            P.eliminate_zeros()
            if normal is False:
                P.data = np.clip(P.data * scaling_factor, 0, 1)
                A = sp.csr_matrix((rng.binomial(1, P.data), P.indices, P.indptr), shape=P.shape)
            else:
                P.data = rng.poisson(P.data * scaling_factor)
                A = P
            # If not a multigraph, clip counts to 1 (binary adjacency).
            if not multigraph:
                A.data = np.minimum(A.data, 1)
            # Generate graph from adjacency matrix.
            G = from_scipy_sparse_array(A, parallel_edges=multigraph, create_using=create_using)

        else:
            # Community assignment matrix.
            C = np.zeros((n_nodes, n_clusters))
            C[np.arange(n_nodes), communities] = 1
            # We decompose the matrix multiplications Θ_out · C · B · C^T · Θ_in for efficiency.
            P = np.dot(C, B)
            P = np.dot(P, C.T)
            # Remove self-loops if specified.
            if not selfloops:
                np.fill_diagonal(P, 0)
            # Take upper triangle for undirected graphs.
            if not directed:
                P = np.triu(P)
            # Sample edges from distribution.
            if d is not None:
                # Degree-correction factors.
                P = np.multiply(theta_out[:, None], P)
                P = np.multiply(P, theta_in[None, :])
            # Scaling with clipping so probabilities are in [0, 1] if Bernoulli sampling.
            total_expected_edges = P.sum()
            total_target_edges = sum(d_in + d_out) if deg is not None else total_expected_edges
            scaling_factor = total_target_edges / total_expected_edges
            if normal is False:
                P.data = np.clip(P.data * scaling_factor, 0, 1).flatten()
                A = np.array(rng.binomial(1, P.flatten())).reshape(P.shape)
            else:
                A = rng.poisson(P * scaling_factor)
            # If not a multigraph, clip counts to 1 (binary adjacency).
            if not multigraph:
                A = np.minimum(A, 1)
            # Generate graph from adjacency matrix.
            G = nx.from_numpy_array(A, parallel_edges=multigraph, create_using=create_using)

        if not isolates:
            G.remove_nodes_from(list(nx.isolates(G)))

        G = nx.relabel_nodes(G, mapping={n: int(n) for n in G.nodes()})
        nx.set_node_attributes(G, {n: int(c) for n, c in zip(G.nodes(), communities)}, "community")
        nx.set_edge_attributes(G, ti, "time")
        TG.append(G)

    return TG
