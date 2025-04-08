from functools import reduce
from typing import Any, Optional, Union

from ..transform import from_static
from ..typing import TemporalGraph, StaticGraph, Literal
from ..utils import is_static_graph


def degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node degrees. Defined as the sum of degrees across time:

    .. math::

        \\text{deg}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij} + \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight``.

    In case of multigraphs, :math:`\\mathbf{A}` is weighted to consider parallel edges,
    unless ``weight=False``.

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.degree`
        and :func:`~networkx_temporal.graph.TemporalGraph.total_degree`.
    """
    return _degree(TG, degree="degree", nbunch=nbunch, weight=weight)


def in_degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node in-degrees. Defined as the sum of in-degrees across time:

    .. math::

        \\text{deg}_{\\text{in}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight``.

    In case of multigraphs, :math:`\\mathbf{A}` is weighted to consider parallel edges,
    unless ``weight=False``.

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.in_degree`
        and :func:`~networkx_temporal.graph.TemporalGraph.total_in_degree`.
    """
    return _degree(TG, degree="in_degree", nbunch=nbunch, weight=weight)


def out_degree(
    TG: Union[TemporalGraph, StaticGraph],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node out-degrees. Defined as the sum of out-degrees across time:

    .. math::

        \\text{deg}_{\\text{out}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij},

    where :math:`i` is a node,
    :math:`j` is a node in the neighborhood :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix, optionally weighted by an edge-level
    ``weight``.

    In case of multigraphs, :math:`\\mathbf{A}` is weighted to consider parallel edges,
    unless ``weight=False``.

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Aliases:
        :func:`~networkx_temporal.algorithms.out_degree`
        and :func:`~networkx_temporal.graph.TemporalGraph.total_out_degree`.
    """
    return _degree(TG, degree="out_degree", nbunch=nbunch, weight=weight)


def _degree(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:

    assert degree in ("degree", "in_degree", "out_degree"),\
        f"Argument `degree` must be one of ('degree', 'in_degree', 'out_degree')."

    if TG.is_multigraph() and weight is False:
        TG = from_multigraph(TG, weight=False)

    degrees = [
        getattr(G, degree)(nbunch=nbunch, weight=weight)
        for G in ([TG] if is_static_graph(TG) else TG)
    ]

    if nbunch is not None and any(type(d) == int for d in degrees):
        return sum([d for d in degrees if type(d) == int]) or None

    sorted_degrees = {}
    for deg in degrees:
        for n, d in dict(deg).items():
            sorted_degrees[n] = sorted_degrees.get(n, 0) + d

    return sorted_degrees or None

