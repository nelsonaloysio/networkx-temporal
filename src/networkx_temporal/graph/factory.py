from typing import Optional, Union

import networkx as nx

from ..typing import TemporalGraph


def temporal_graph(
    t: Optional[int] = None,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]] = None,
) -> TemporalGraph:
    """
    Returns an empty temporal graph with the desired properties.

    This is a factory method for temporal graphs. It returns a
    :class:`~networkx_temporal.TemporalGraph`, :class:`~networkx_temporal.TemporalDiGraph`,
    :class:`~networkx_temporal.TemporalMultiGraph`, or :class:`~networkx_temporal.TemporalMultiDiGraph`
    object, depending on the choice of parameters.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.
    :param directed: If ``True``, inherits a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__.
        Defaults to ``False``.
    :param multigraph: If ``True``, inherits a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__.
        Defaults to ``False``.
    :param object create_using: NetworkX graph object to use as template. Optional.
        Does not allow ``directed`` and ``multigraph`` parameters when set.

    :rtype: TemporalGraph
    """
    assert directed is None or type(directed) == bool,\
        f"Argument `directed` must be a boolean, received: {type(directed)}."
    assert multigraph is None or type(multigraph) == bool,\
        f"Argument `multigraph` must be a boolean, received: {type(multigraph)}."
    assert create_using is None or type(create_using) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `create_using` must be a NetworkX graph object, received: {type(create_using)}."
    assert create_using is None or (directed is None and multigraph is None),\
        "Arguments `directed` and `multigraph` should be `None` when `create_using` is given."

    if create_using is not None:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()

    from . import TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    return locals()[f"Temporal{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph"](t=t)
