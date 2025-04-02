from functools import reduce
from typing import Any, Optional, Union

from ...utils import is_static_graph, _dict, _sum


def degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node degrees. Defined as:

    .. math::

        \\text{deg}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij} + \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in its set of neighbors :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix (optionally weighted by the edge-level
    ``weight`` attribute value).
    In case of multigraphs, :math:`\\mathbf{A}` is always weighted to consider parallel edges,
    unless ``weight=False``.

    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Equivalent to the method :func:`~networkx_temporal.graph.TemporalGraph.total_degree`
        in :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    if is_static_graph(self):
        return self.degree(nbunch=nbunch, weight=weight)
    # if self.is_multigraph() and weight is False:
    #     return _dict(reduce(or_, from_multigraph(self, weight=False).degree(nbunch=nbunch)))
    return _dict(reduce(_sum, self.degree(nbunch=nbunch, weight=weight)))


def in_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node in-degrees. Defined as:

    .. math::

        \\text{deg}_{\\text{in}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ji},

    where :math:`i` is a node,
    :math:`j` is a node in its set of neighbors :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix (optionally weighted by the edge-level
    ``weight`` attribute value).
    In case of multigraphs, :math:`\\mathbf{A}` is always weighted to consider parallel edges,
    unless ``weight=False``.

    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Equivalent to the method :func:`~networkx_temporal.graph.TemporalGraph.total_in_degree`
        in :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    if is_static_graph(self):
        return self.in_degree(nbunch=nbunch, weight=weight)
    return _dict(reduce(_sum, self.in_degree(nbunch=nbunch, weight=weight)))


def out_degree(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node out-degrees. Defined as:

    .. math::

        \\text{deg}_{\\text{out}}(i) =
        \\sum_{G \\in \\mathcal{G}} \\sum_{j \\in \\mathcal{N}(i)} \\mathbf{A}_{ij},

    where :math:`i` is a node,
    :math:`j` is a node in its set of neighbors :math:`\\mathcal{N}(i)`,
    :math:`G` is a snapshot in the temporal graph :math:`\\mathcal{G}`,
    and :math:`\\mathbf{A}` is the adjacency matrix (optionally weighted by the edge-level
    ``weight`` attribute value).
    In case of multigraphs, :math:`\\mathbf{A}` is always weighted to consider parallel edges,
    unless ``weight=False``.

    :param nbunch: One or more nodes to return. Optional.
    :param weight: Edge attribute key to consider. Optional.

    :note: Equivalent to the method :func:`~networkx_temporal.graph.TemporalGraph.total_out_degree`
        in :class:`~networkx_temporal.graph.TemporalGraph` objects.
    """
    if is_static_graph(self):
        return self.out_degree(nbunch=nbunch, weight=weight)
    return _dict(reduce(_sum, self.out_degree(nbunch=nbunch, weight=weight)))
