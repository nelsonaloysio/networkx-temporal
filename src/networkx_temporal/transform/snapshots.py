from typing import Optional, Union

from ..typing import TemporalGraph
from ..utils import is_static_graph
from ..utils.convert import convert, FORMATS


def from_snapshots(graphs: Union[dict, list]) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.classes.TemporalGraph` from sequence of snapshots.

    .. seealso::

        The `Convert and transform → Graph representations
        <../examples/convert.html#graph-representations>`__
        page for details and examples.

    :param graphs: List or dictionary of NetworkX graphs.
    """
    T = list(graphs.keys()) if type(graphs) == dict else range(len(graphs))

    directed = graphs[T[0]].is_directed()
    multigraph = graphs[T[0]].is_multigraph()

    assert type(graphs) in (dict, list),\
        "Argument `graphs` must be a list or dictionary of NetworkX graphs."
    assert len(graphs) > 0,\
        "Argument `graphs` must be a non-empty list or dictionary."
    assert all(is_static_graph(graphs[t]) for t in T),\
        "All elements in data must be valid NetworkX graphs."
    assert all(directed == graphs[T[t]].is_directed() for t in T),\
        "Mixed graphs and digraphs are not supported."
    assert all(multigraph == graphs[T[t]].is_multigraph() for t in T),\
        "Mixed graphs and multigraphs are not supported."

    from ..classes import temporal_graph
    TG = temporal_graph(directed=directed, multigraph=multigraph)
    TG.data = graphs
    return TG


def to_snapshots(TG: TemporalGraph, to: Optional[FORMATS] = None, as_view: bool = True) -> list:
    """
    Returns a list of snapshots. Each snapshot is a view of the original graph, which can be
    converted to a different format using the ``to`` argument, if desired.

    .. note::

        Internally, :class:`~networkx_temporal.classes.TemporalGraph` already stores data as a
        list of graph views on :func:`~networkx_temporal.classes.TemporalGraph.slice`. This method
        simply returns the underlying data, unless :func:`~networkx_temporal.utils.convert.convert`
        is called by setting ``to``.

    :param TemporalGraph TG: Temporal graph object.
    :param str to: Package name or alias to convert the graph object
        (see :func:`~networkx_temporal.utils.convert.convert`). Optional.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.

    :note: Available both as a function and as a method from :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    if not as_view and to is not None:
        return [G.copy() for G in TG.data]
    if to is not None:
        return [convert(G, to) for G in TG.data]
    return TG.data
