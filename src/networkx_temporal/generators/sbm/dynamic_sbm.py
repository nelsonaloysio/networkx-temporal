from typing import List, Optional, Union
from warnings import warn

import networkx as nx
import numpy as np
import scipy.sparse as sp

from ..generators import transition_node_memberships
from ...classes.factory import empty_graph
from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import Literal, TemporalGraph, StaticGraph

try:
    from networkx import from_scipy_sparse_array
except ImportError:
    from networkx import from_scipy_sparse_matrix as from_scipy_sparse_array

DISTRIBUTION = Literal["poisson", "bernoulli"]
DISTRIBUTIONS = DISTRIBUTION.__args__


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
    create_using: Optional[Union[TemporalGraph, StaticGraph]] = None,
    distribution: DISTRIBUTION = "poisson",
    sparse: Optional[bool] = False,
    seed: Optional[int] = None,
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
    are sampled from a Poisson (default) or Bernoulli (if ``distribution='bernoulli'``)
    distribution considering the temporal communities :math:`\\mathbf{z}^{(t)}`.

    .. math::

        \\mathbb{P}(
        \\mathbf{A}^{(t)} \\vert \\mathbf{B}, \\mathbf{z}^{(t)}, \\mathbf{d}, \\mathbf{d_{out}}) =
        \\mathbf{\\Theta_{out}} \\; \\mathbf{C} \\; \\mathbf{B} \\;
        \\mathbf{C}^\\text{T} \\; \\mathbf{\\Theta_{in}},

    where :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix and
    :math:`\\mathbf{\\Theta}` are diagonal matrices of degree-correction factors given by the
    inverse square root of the sum of expected node degrees.
    Degree-correction factors are computed based on the expected degree vectors, which are
    fixed over time, and not based on the actual degree of nodes at each snapshot.

    Under the Poisson model, edge multiplicities are drawn as counts, yielding a multigraph;
    set ``multigraph=False`` to collapse counts to a binary adjacency. Note that the Bernoulli
    model and ``min(Poisson, 1)`` are *not* equivalent at non-vanishing density: collapsing
    Poisson counts yields :math:`\\text{Bernoulli}(1 - e^{-\\lambda})`, not
    :math:`\\text{Bernoulli}(\\lambda)`. Use ``distribution='bernoulli'`` for a true
    simple-graph SBM in the dense regime.

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

        TemporalMultiGraph (t=4) with 32 nodes and 97 edges

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
        `tadc-sbm <https://github.com/nelsonaloysio/tadcsbm>`__.

    .. [1] Amir Ghasemian et al. (2016).
        ''Detectability Thresholds and Optimal Algorithms for Community Structure in Dynamic
        Networks''. doi: `10.1103/PhysRevX.6.031005 <https://doi.org/10.1103/PhysRevX.6.031005>`__

    :param B: Block matrix with edge probabilities (Bernoulli) or rates (Poisson).
    :param z: Community vector assigning nodes to clusters.
    :param d: Vector of expected node degrees.
        For directed graphs, this sets the in-degree vector.
    :param d_out: Expected node out-degrees vector (for asymmetric directed graphs).
        For directed graphs, if unset, out-degrees default to the in-degree vector ``d``.
        For undirected graphs, this parameter is ignored.
    :param t: Number of snapshots to generate.
    :param transition_matrix: Transition matrix used for snapshots.
        If unset, nodes do not transition communities over time.
    :param directed: Whether edges are directed. Defaults to ``False``.
    :param multigraph: Allows parallel edges. Defaults to ``True``.
    :param isolates: Allows isolated nodes. Default is ``True``.
        If ``False``, nodes are re-indexed after removing isolates from graph.
    :param selfloops: Allows self-loops. Default is ``False``.
    :param create_using: Graph constructor to use.
    :param fix_transition_prob: If ``True``, node transition probabilities refer
        to the ground truth probabilities in every snapshot. Default is ``False``.
    :param distribution: Edge sampling distribution, either ``'poisson'`` (default) or
        ``'bernoulli'``. Poisson yields edge counts (a multigraph); Bernoulli yields a
        simple graph and requires ``B`` entries in ``[0, 1]``.
    :param sparse: Whether to build each snapshot from a sparse adjacency matrix. This affects
        the output representation only; the rate matrix is always dense. Default is ``False``.
    :param seed: Random number generator state.

    :note: Alias to :func:`~networkx_temporal.generators.dynamic_sbm`.
    """
    if not (t is None or (type(t) == int and t > 0)):
        raise ValueError("Number of snapshots `t` must be a positive integer.")
    if create_using is not None:
        if not is_static_graph(create_using) and not is_temporal_graph(create_using):
            raise TypeError("Expected a static or temporal graph object for `create_using`.")
        if not multigraph is None and directed is None:
            raise ValueError(
                "Parameters `multigraph` and `directed` are exclusive with `create_using`."
            )

    # Block matrix as a dense float array (k x k, always small).
    B = B.toarray() if sp.issparse(B) else np.asarray(B, dtype=float)
    if B.ndim != 2 or B.shape[0] != B.shape[1]:
        raise ValueError("Block matrix `B` must be square.")

    if distribution == "poisson":
        if np.any(B < 0):
            raise ValueError("Block matrix `B` must be non-negative for Poisson.")
    elif distribution == "bernoulli":
        if np.any(B < 0) or np.any(B > 1):
            raise ValueError("Block matrix `B` must have probabilities in [0, 1] for Bernoulli.")
    else:
        raise ValueError(f"Invalid distribution '{distribution}'. Must be one of {DISTRIBUTIONS}.")

    communities = z
    if len(z) < 1:
        raise ValueError("Community vector `z` must have at least one node.")
    if any(c < 0 or c >= len(B) for c in z):
        raise ValueError("Community vector `z` contains invalid community indices.")

    tau = transition_matrix
    if tau is not None and (len(tau) != len(B) or len(tau[0]) != len(B[0])):
        raise ValueError("Transition matrix `tau` must match block matrix `B` shape.")
    if tau is not None:
        tau_values = np.asarray(tau)
        if np.any(tau_values < 0):
            raise ValueError("Transition matrix `tau` must be nonnegative.")
        row_sums = tau_values.sum(axis=1)
        if not np.allclose(row_sums, 1):
            raise ValueError("Transition matrix `tau` rows must sum to 1.")

    deg = d
    if d is not None and (len(z) != len(d) or (d_out is not None and len(d) != len(d_out))):
        raise ValueError("Communities `z` length differs from degree vectors `deg` or `deg_out`.")

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
                d_out = d_in.copy()
        else:
            d_in = d_out = np.array(deg)
        theta_in = d_in / np.sqrt(np.sum(d_in))
        theta_out = d_out / np.sqrt(np.sum(d_out))

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

        comm = np.asarray(communities)

        # Rate/probability matrix P[i, j] = B[z_i, z_j], i.e. Θ_out · C · B · C^T · Θ_in.
        # Since C is one-hot, the matrix product is a block gather (avoids forming C explicitly).
        P = B[np.ix_(comm, comm)].astype(float, copy=True)

        # Remove self-loops if specified.
        if not selfloops:
            np.fill_diagonal(P, 0.0)
        # Take upper triangle for undirected graphs (one draw per unordered pair).
        if not directed:
            P = np.triu(P)
        # Degree-correction factors (fixed expected degrees, not per-snapshot degrees).
        if deg is not None:
            P *= theta_out[:, None]
            P *= theta_in[None, :]

        # Rescale so the expected edge count matches the target degree sum.
        total_expected_edges = float(P.sum())
        if deg is not None:
            total_target_edges = float(np.sum(d_out)) if directed else float(np.sum(d_in)) / 2.0
        else:
            total_target_edges = total_expected_edges
        scaling_factor = 0.0 if total_expected_edges <= 0 else (
            total_target_edges / total_expected_edges)
        P *= scaling_factor

        # Sample the adjacency matrix from the chosen distribution.
        if distribution == "poisson":
            A = rng.poisson(P)
        elif distribution == "bernoulli":
            np.clip(P, 0.0, 1.0, out=P)
            A = rng.binomial(1, P)

        # Collapse parallel edges for simple graphs.
        if not multigraph:
            A = np.minimum(A, 1)

        # Build the snapshot graph from the adjacency matrix.
        if sparse:
            # NOTE: CSR from dense array stores no explicit zeros.
            A = sp.csr_matrix(A)
            G = from_scipy_sparse_array(A, parallel_edges=multigraph, create_using=create_using)
        else:
            G = nx.from_numpy_array(A, parallel_edges=multigraph, create_using=create_using)

        G = nx.relabel_nodes(G, mapping={n: int(n) for n in G.nodes()})
        nx.set_node_attributes(
            G,
            {n: int(comm[n]) for n in G.nodes()},
            "community"
        )
        nx.set_edge_attributes(G, ti, "time")
        if not isolates:
            G.remove_nodes_from(list(nx.isolates(G)))
        TG.append(G)

    if not isolates:
        # Re-index nodes after removing isolates.
        mapping = {n: i for i, n in enumerate(dict.fromkeys(TG.temporal_nodes(copies=True)))}
        TG.graphs = list(map(lambda G: nx.relabel_nodes(G, mapping, copy=True), TG))

    return TG