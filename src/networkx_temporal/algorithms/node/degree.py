from functools import reduce
from typing import Any, Optional, Union

import networkx as nx

from ...typing import TemporalGraph, StaticGraph, Literal
from ...utils import is_static_graph


def degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns node degrees.
    Defined [2]_ for temporal graphs as the sum of node degrees across time:

    .. math::

        \\text{deg}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij} + \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight`` attribute. For multigraphs, adjacencies are weighted by the number of
    parallel edges, unless ``weight=False``.

    .. [2] Hyoungshick, K., Anderson, R. (2012).
           Temporal node centrality in complex networks.
           Physical Review E, 85(2).
           doi: `10.1103/PhysRevE.85.026107 <https://doi.org/10.1103/PhysRevE.85.026107>`__

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.degree`
        and :func:`~networkx_temporal.classes.TemporalGraph.total_degree`.
    """
    return _degree_total(TG, degree="degree", nbunch=nbunch, weight=weight)


def in_degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns node in-degrees.
    Defined [2]_ for temporal graphs as the sum of node in-degrees across time:

    .. math::

        \\text{deg}_{\\text{in}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight`` attribute. For multigraphs, adjacencies are weighted by the number of
    parallel edges, unless ``weight=False``.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.in_degree`
        and :func:`~networkx_temporal.classes.TemporalGraph.total_in_degree`.
    """
    return _degree_total(TG, degree="in_degree", nbunch=nbunch, weight=weight)


def out_degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns node out-degrees.
    Defined [2]_ for temporal graphs as the sum of node out-degrees across time:

    .. math::

        \\text{deg}_{\\text{out}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight`` attribute. For multigraphs, adjacencies are weighted by the number of
    parallel edges, unless ``weight=False``.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.out_degree`
        and :func:`~networkx_temporal.classes.TemporalGraph.total_out_degree`.
    """
    return _degree_total(TG, degree="out_degree", nbunch=nbunch, weight=weight)


def degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
) -> Union[dict, int]:
    """
    Returns node degree centralities.
    Defined [2]_ as the fraction of connected nodes, i.e.,

    .. math::

        c_{\\text{deg}}(i) =
        \\frac{\\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij} + \\mathbf{A}_{ji}}
        {|\\mathcal{V}|},

    where
    :math:`c_{\\text{deg}}(i)` is the degree centrality of node :math:`i`,,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`\\mathbf{A}` is the adjacency matrix,
    and :math:`|\\mathcal{V}|` is the order of the graph :math:`\\mathcal{G}`.
    Note that this function does not consider node copies or edge weights in the adjacency matrix.

    :param nbunch: One or more nodes to return. Optional.
    """
    return _degree_centrality(TG, degree="degree", nbunch=nbunch)


def in_degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
) -> Union[dict, int]:
    """
    Returns node in-degree centralities.
    Defined [1]_ as the fraction of connected nodes, i.e.,

    .. math::

        c_{\\text{in}}(i) =
        \\frac{\\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ji}}
        {|\\mathcal{V}|},

    where
    :math:`c_{\\text{in}}(i)` is the degree centrality of node :math:`i`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`\\mathbf{A}` is the adjacency matrix,
    and :math:`|\\mathcal{V}|` is the order of the graph :math:`\\mathcal{G}`.
    Note that this function does not consider node copies or edge weights in the adjacency matrix.

    :param nbunch: One or more nodes to return. Optional.
    """
    return _degree_centrality(TG, degree="in_degree", nbunch=nbunch)


def out_degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
) -> Union[dict, int]:
    """
    Returns node out-degree centralities.
    Defined [1]_ as the fraction of connected nodes, i.e.,

    .. math::

        c_{\\text{out}}(i) =
        \\frac{\\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij}}
        {|\\mathcal{V}|},

    where
    :math:`c_{\\text{in}}(i)` is the degree centrality of node :math:`i`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`\\mathbf{A}` is the adjacency matrix,
    and :math:`|\\mathcal{V}|` is the order of the graph :math:`\\mathcal{G}`.
    Note that this function does not consider node copies or edge weights in the adjacency matrix.

    :param nbunch: One or more nodes to return. Optional.
    """
    return _degree_centrality(TG, degree="out_degree", nbunch=nbunch)


def _degree_total(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None,
) -> Union[dict, int]:

    assert degree in ("degree", "in_degree", "out_degree"),\
        f"Argument `degree` must be one of ('degree', 'in_degree', 'out_degree')."

    if TG.is_multigraph() and weight is False:
        TG = from_multigraph(TG, weight=False)

    degrees = getattr(TG, degree)(nbunch=nbunch, weight=weight)

    if nbunch is not None and any(type(d) == int for d in degrees):
        return sum([d for d in degrees if type(d) == int])

    degree_sum = {}
    for deg in degrees:
        if deg is None:
            continue
        for n, d in deg:
            degree_sum[n] = degree_sum.get(n, 0) + d

    return degree_sum


def _degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None,
) -> Union[dict, float]:

    assert degree in ("degree", "in_degree", "out_degree"), \
        f"Invalid `degree`: expects 'degree', 'in_degree', or 'out_degree'."

    degrees = _degree_total(TG, degree=degree, nbunch=nbunch, weight=weight)

    order = len(
        reduce(
            lambda x, y: x.union(y),
            [set(G.nodes()) for G in ([TG] if is_static_graph(TG) else TG)]
        )
    )

    if type(degrees) == int:
        return degrees / (order - 1)

    return {
        node: d / (order - 1)
        for node, d in degrees.items()
    }
