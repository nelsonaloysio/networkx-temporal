from functools import reduce
from operator import or_
from typing import Any, Optional, Union
from warnings import warn

from ...utils import from_multigraph, _dict, _sum


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
    if self.is_multigraph() and weight is False:
        return _dict(reduce(or_, from_multigraph(self, weight=False).degree(nbunch=nbunch)))
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
    return _dict(reduce(_sum, self.out_degree(nbunch=nbunch, weight=weight)))


def _temporal_degree(self, *args, **kwargs) -> list:
    """
    Deprecated in favor of :func:`~networkx_temporal.metrics.node.degree`.

    :meta private:
    """
    warn("Function `temporal_degree` deprecated in favor of `total_degree`.")
    return self.total_degree(*args, **kwargs)


def _temporal_in_degree(self, *args, **kwargs) -> list:
    """
    Deprecated in favor of :func:`~networkx_temporal.metrics.node.in_degree`.

    :meta private:
    """
    warn("Function `temporal_in_degree` deprecated in favor of `total_in_degree`.")
    return self.total_in_degree(*args, **kwargs)


def _temporal_out_degree(self, *args, **kwargs) -> list:
    """
    Deprecated in favor of :func:`~networkx_temporal.metrics.node.out_degree`.

    :meta private:
    """
    warn("Function `temporal_out_degree` deprecated in favor of `total_out_degree`.")
    return self.total_out_degree(*args, **kwargs)
