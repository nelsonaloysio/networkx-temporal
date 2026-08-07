from typing import Optional, Union

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import TemporalGraph
from ..utils.convert import convert
from ..utils.convert.convert import FORMAT

from networkx import NetworkXError


def from_snapshots(graphs: Union[dict, list]) -> TemporalGraph:
    """ Returns :class:`~networkx_temporal.classes.TemporalGraph` from snapshots.

    .. seealso::

        The `Convert and transform → Graph representations
        <../examples/convert.html#graph-representations>`__
        page for details and examples.

    :param graphs: List or dictionary of NetworkX graphs.
    """
    T = list(graphs.keys()) if type(graphs) == dict else range(len(graphs))

    if not all(is_static_graph(graphs[t]) or is_temporal_graph(graphs[t]) for t in T):
        raise TypeError("All elements in data must be valid NetworkX graphs.")

    directed = graphs[T[0]].is_directed()
    if any(directed != graphs[t].is_directed() for t in T):
        raise NetworkXError("Mixed graphs and digraphs are not supported.")

    multigraph = graphs[T[0]].is_multigraph()
    if any(multigraph != graphs[t].is_multigraph() for t in T):
        raise NetworkXError("Mixed graphs and multigraphs are not supported.")

    from .. import empty_graph
    TG = empty_graph(directed=directed, multigraph=multigraph)
    list(TG.add_snapshot(graphs[t]) if is_static_graph(graphs[t]) else TG.add_snapshots_from(graphs[t]) for t in T)
    TG.index = list(T) if type(graphs) == dict else None
    return TG


def to_snapshots(TG: TemporalGraph, to: Optional[FORMAT] = None, as_view: bool = True) -> list:
    """ Returns a list of snapshots. Each snapshot is a view of the original graph, which can be
    converted to a different format using the ``to`` argument, if desired.

    .. note::

        Internally, :class:`~networkx_temporal.classes.TemporalGraph` already stores data as a
        list of graph views on :func:`~networkx_temporal.classes.TemporalGraph.slice`. This method
        simply returns the underlying data, unless :func:`~networkx_temporal.utils.convert`
        is called by setting ``to``.

    :param TemporalGraph TG: Temporal graph object.
    :param str to: Package name or alias to convert the graph object
        (see :func:`~networkx_temporal.utils.convert`). Optional.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    if not as_view and to is not None:
        return [G.copy() for G in TG.graphs]
    if to is not None:
        return [convert(G, to) for G in TG.graphs]
    return TG.graphs
