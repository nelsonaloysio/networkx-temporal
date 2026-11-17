from typing import List, Optional, Union

import networkx as nx
import numpy as np
import scipy.sparse as sp

from ...classes import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph
from ...utils import map_attr_to_nodes, partition_nodes
from ...utils.convert import to_numpy, to_scipy
from typing import Optional, Union


def modularity(
    graph: Union[TemporalGraph, StaticGraph],
    communities: Union[str, list, dict],
    weight: Optional[str] = "weight",
    resolution: Optional[float] = 1,
    spectral: bool = False,
    sparse: bool = False,
) -> Union[float, List[float]]:
    """ Returns the modularity of a graph.

    Modularity [8]_ measures the fraction of edges in a graph that fall within communities,
    compared to their expected number in a random graph with the same degree sequence.
    Higher values may indicate more internal connections than expected by chance.
    It is commonly defined as:

    .. math::

        Q =
        \\frac{1}{2m} \\sum_{(i,j) \\in V^2}
        \\left[ A_{ij} - \\gamma \\frac{d_i^{out} \\, d_j^{in}}{2m} \\right]
        \\delta(c_i, c_j),

    where
    :math:`m` is the number of edges in the graph,
    :math:`(i,j) \\in V^2` are node pairs,
    :math:`\\mathbf{A}` is the adjacency matrix,
    :math:`d` are node in/out-degrees,
    :math:`c` are their communities,
    and :math:`\\gamma = 1` (default) is the resolution parameter [4]_,
    where smaller values favor larger communities, including negative values.

    This can be reduced to a summation over communities, which is more efficient to compute:

    .. math::

        Q = \\sum_{c \\in C} \\left[ \\frac{L_c}{m} - \\gamma
        \\left( \\frac{d_c}{2m} \\right)^2 \\right],

    where :math:`L_c` is the number of within-community edges
    :math:`d_c` is the sum of degrees of nodes in community :math:`c`,
    :math:`C` is the set of communities,
    and :math:`\\gamma` is the resolution parameter.
    If ``spectral=True``, modularity is computed using
    :func:`~networkx_temporal.algorithms.modularity_spectral` instead.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.modularity_multislice` function for a temporal
        generalization of the metric.

    .. [8] A. Clauset, M. E. J. Newman, C. Moore (2004). Finding community structure in very
        large networks. Phys. Rev. E 70.6 (2004).
        doi: `10.1103/PhysRevE.70.066111 <https://doi.org/10.1103/PhysRevE.70.066111>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param communities: String (node attribute key), list of community assignments,
        or dict mapping node to community.
    :param resolution: Resolution parameter :math:`\\gamma = 1` (default).
        Controls the size of communities, where higher values lead to smaller communities.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param spectral: Whether to use the spectral method to compute modularity.
        If ``False``, use `NetworkX modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__
        (default).
    :param sparse: Whether to use a sparse matrix representation for the spectral method.
        Only applicable if ``spectral=True``. Default is ``False``.
    """
    resolution = 1 if resolution is None else resolution

    if not is_static_graph(graph) and not is_temporal_graph(graph):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if type(resolution) not in (int, float):
        raise TypeError("Resolution expects a numeric value.")
    if weight is not None and type(weight) != str:
        raise TypeError("Weight expects a string.")

    if spectral:
        fnc = modularity_spectral
        kwargs = {"weight": weight, "gamma": resolution, "directed": graph.is_directed()}
        assignments = communities
        if type(communities) in (str, dict):
            # Map to (n,) array or (n, k) matrix.
            assignments = map_attr_to_nodes(graph, communities, index=False)
        to_matrix = to_scipy if sparse else to_numpy
        if is_static_graph(graph) or is_temporal_graph(graph):
            graph = to_matrix(graph, weight=weight)
        return fnc(graph, assignments, **kwargs)

    else:
        fnc = nx.algorithms.community.quality.modularity
        kwargs = {"weight": weight, "resolution": resolution}
        assignments = partition_nodes(graph, communities, index=False)

    if is_static_graph(graph):
        return fnc(graph, assignments, **kwargs)

    return [fnc(g, z, **kwargs) for g, z in zip(graph, assignments)]


def modularity_multislice(
    TG: TemporalGraph,
    communities: Union[list, str, dict],
    resolution: Optional[float] = 1.0,
    interslice_weight: Optional[float] = 1.0,
    weight: Optional[str] = "weight",
    spectral: bool = False
) -> float:
    """ Returns the MS-modularity of a temporal graph.

    Multislice modularity [9]_ is a generalization of the metric for multiplex graphs, where each
    layer corresponds to a temporal graph snapshot. Temporal node copies are connected across time
    by interlayer edges ("couplings"), as in an `unrolled graph
    <../examples/convert.html#unrolled-temporal-graph>`__, so the expected fraction of intra-layer
    edges is adjusted to account for these added connections. It may be defined as:

    .. math::

        Q_\\mathrm{MS} =
        \\frac{1}{2\\mu}
        \\sum_{i,j,s,r}
        \\left[
            \\left(
                A_{ij}^{(s)} - \\gamma^{(s)} \\frac{k_i^{(s)} k_j^{(s)}}{2m^{(s)}}
            \\right)
            \\delta^{(sr)}
            + \\delta_{ij}\\,\\omega^{(sr)}
        \\right]
        \\delta(c_i^{(s)}, c_j^{(r)}),

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

    .. [9] P. J. Mucha et al. (2010). Community Structure in Time-Dependent,
       Multiscale, and Multiplex Networks. Science, 328, 876--878.
       doi: `10.1126/science.1184819 <https://doi.org/10.1126/science.1184819>`__.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param communities: String (node attribute name), list of community assignments,
        or list of such lists (for temporal graphs).
    :param resolution: Resolution parameter :math:`\\gamma = 1` (default).
        Controls the size of communities, where higher values lead to smaller communities.
    :param interslice_weight: The interlayer edge weight. Default is ``1``.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param spectral: Whether to use the spectral method to compute intra-slice modularity.
        If ``False`` (default), use `NetworkX modularity
        <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.quality.modularity.html>`__.
    """
    interslice_weight = 1 if interslice_weight is None else interslice_weight

    if not is_temporal_graph(TG):
        raise TypeError(f"Expects a temporal graph object, received: {type(TG)}.")

    Q = modularity(
        TG,
        communities,
        weight=weight,
        resolution=resolution,
        spectral=spectral,
    )

    labels = map_attr_to_nodes(TG, communities)

    # Count node appearances over time.
    temporal_nodes = {}
    for G in TG:
        for node in G:
            temporal_nodes[node] = temporal_nodes.get(node, 0) + 1

    interslice_edges = sum(
        count - 1
        for count in temporal_nodes.values()
    )

    # Combine intra- and inter-slice modularity contributions.
    coupling = sum(
        1
        for t in range(len(TG)-1)
        for n in set(TG[t]) & set(TG[t+1])
        if labels[t][n] == labels[t+1][n]
    )

    # Total number of edges (intra- + inter-slice).
    intra = sum(q * 2 * TG[t].size(weight=weight) for t, q in enumerate(Q))
    mu = sum(G.size(weight=weight) for G in TG) + (interslice_weight * interslice_edges)

    return (intra + (interslice_weight * coupling)) / (2 * mu)


def modularity_spectral(
    adj: sp.spmatrix,
    communities: object,
    resolution: Optional[float] = 1,
    directed: Optional[bool] = True,
    weight: Optional[Union[str, bool]] = True,
) -> float:
    """ Calculates modularity on the graph spectrum. Expects a dense or sparse ``adj``
    matrix from :func:`~networkx_temporal.utils.to_numpy` or
    :func:`~networkx_temporal.utils.to_scipy`, respectively.
    Supports mixed-membership (soft) assignments.

    The spectral modularity [10]_ for a matrix of community assignments :math:`\\mathbf{C}` is
    computed as

    .. math::

        \\mathcal{Q} = \\frac{1}{2m} \\mathbf{C}^\\text{T} \\mathbf{B} \\mathbf{C},
        \\quad \\text{with} \\quad
        \\mathbf{B} = \\mathbf{A} - \\gamma
        \\frac{\\mathbf{d_{out}} \\, \\mathbf{d_{in}}^\\text{T}}{2m},

    where
    :math:`m` is the total number of edges,
    :math:`\\mathbf{A}` is the input adjacency matrix,
    :math:`\\mathbf{B}` is the modularity matrix,
    :math:`\\mathbf{C}` is the :math:`n \\times k` community assignment matrix
    with :math:`n` as the number of nodes and :math:`k` the number of communities,
    :math:`\\mathbf{d_{in}}` and :math:`\\mathbf{d_{out}}` are the node in- and out-degree vectors,
    and :math:`\\gamma = 1` (default) is the resolution parameter, where larger values lead to
    smaller communities.

    .. [10] Newman, M. E. J. (2006). Modularity and community structure in networks.
       Proceedings of the National Academy of Sciences, 103(23), 8577-8582.

    :param adj: Adjacency matrix in CSR format. Accepts dense (NumPy) or sparse (SciPy) matrices.
    :param communities: Community assignment matrix with shape ``(n_nodes, k_communities)``,
        a or vector of length ``n_nodes``.
    :param resolution: Resolution parameter :math:`\\gamma = 1` (default).
        Controls the size of communities, where higher values lead to smaller communities.
    :param directed: Whether the graph is directed. Default is ``True``.
    :param weight: Whether to consider edge weights. If a string is provided,
        it is used as the edge attribute key. Default is ``True``.
    """
    if is_static_graph(adj) or is_temporal_graph(adj):
        raise TypeError(
            f"Expected a dense or sparse adjacency matrix, got {type(adj)}."
        )

    gamma = 1 if gamma is None else gamma
    directed = True if directed is None else directed
    weight = True if weight is None else weight

    n_nodes = adj.shape[0]
    communities = np.array(communities)
    k_communities = np.unique(communities).shape[0]

    if not weight:
        adj[adj != 0] = 1

    # Degree vectors (optionally corrected) and outer product.
    if directed:
        d_in = adj.sum(axis=0)
        d_out = adj.sum(axis=1)
    else:
        d_in = d_out = adj.sum(axis=0)
    # Apply correction if provided.
    D = d_out.reshape(-1, 1) @ d_in.reshape(1, -1)

    # Community assignment matrix.
    if communities.ndim == 2:
        C = communities
    elif communities.ndim == 1:
        C = sp.csr_matrix((np.ones(n_nodes), (np.arange(n_nodes), communities)))
    else:
        C = np.zeros((n_nodes, k_communities))
        for c in (communities if type(communities[0]) == list else [communities]):
            C[np.arange(n_nodes), c] += 1

    # Modularity matrix.
    B = adj - ((D * gamma) / ((C.T @ adj @ C).sum()))

    # Compute modularity.
    Q = np.trace((C.T @ B @ C) / adj.sum())

    return float(Q)
