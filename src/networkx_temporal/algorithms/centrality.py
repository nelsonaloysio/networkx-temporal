from functools import reduce
from typing import Any, Optional, Union

from .degree import _degree
from ..typing import Literal, TemporalGraph, StaticGraph
from ..utils import is_static_graph


def degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
) -> Union[dict, int]:
    """
    Returns temporal degree centralities.
    Defined [1]_ as the fraction of connected nodes, i.e.,

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
    Returns temporal in-degree centralities.
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
    Returns temporal out-degree centralities.
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


def _degree_centrality(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    nbunch: Optional[Any] = None,
) -> Union[dict, float]:

    assert degree in ("degree", "in_degree", "out_degree"), \
        f"Invalid `degree`: expects 'degree', 'in_degree', or 'out_degree'."

    degree = _degree(TG, degree=degree, nbunch=nbunch)

    order = len(
        reduce(
            lambda x, y: x.union(y),
            [set(G.nodes()) for G in ([TG] if is_static_graph(TG) else TG)]
        )
    )

    if type(degree) == int:
        return degree / (order - 1)

    return {
        node: d / (order - 1)
        for node, d in degree.items()
    }
