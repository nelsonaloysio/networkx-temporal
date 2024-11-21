from typing import Optional

from .base import is_temporal_graph
from ..typing import TemporalGraph, StaticGraph


def temporal_graph(
    t: Optional[int] = None,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[StaticGraph] = None,
) -> TemporalGraph:
    """
    Creates a temporal graph with the desired properties. Similar to
    `empty_graph <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.empty_graph.html>`__
    from NetworkX.

    This is a factory method for temporal graphs. It returns a
    :class:`~networkx_temporal.graph.TemporalGraph`,
    :class:`~networkx_temporal.graph.TemporalDiGraph`,
    :class:`~networkx_temporal.graph.TemporalMultiGraph`, or
    :class:`~networkx_temporal.graph.TemporalMultiDiGraph`
    object, depending on the choice of parameters.

    .. rubric:: Example

    Creating an empty temporal directed multigraph with a single snapshot:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(directed=True, multigraph=True)
        >>> print(TG)

        TemporalMultiDiGraph (t=1) with 0 nodes and 0 edges

    :param int t: Number of snapshots to initialize. Optional. Default is ``1``.
    :param directed: If ``True``, inherits a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__.
        Defaults to ``False``.
    :param multigraph: If ``True``, inherits a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__.
        Defaults to ``True``.
    :param object create_using: NetworkX or :class:`~networkx_temporal.graph.TemporalGraph` to use
        as template. Optional. Does not allow setting ``directed`` and ``multigraph`` if passed.

    :rtype: TemporalGraph
    """
    assert directed is None or type(directed) == bool,\
        f"Argument `directed` must be a boolean, received: {type(directed)}."
    assert multigraph is None or type(multigraph) == bool,\
        f"Argument `multigraph` must be a boolean, received: {type(multigraph)}."
    assert create_using is None or is_temporal_graph(create_using) or type(create_using) in (AnyStaticGraph.__args__),\
        f"Argument `create_using` must be a NetworkX static or temporal graph object, received: {type(create_using)}."
    assert create_using is None or (directed is None and multigraph is None),\
        "Arguments `directed` and `multigraph` should be unset if `create_using` is given."

    if multigraph is None:
        multigraph = True

    if create_using is not None:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()

    from . import TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    return locals()[f"Temporal{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph"](t=t)
