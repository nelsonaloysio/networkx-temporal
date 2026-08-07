from typing import Optional, Union

import networkx as nx

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph
from ..utils.convert import convert
from ..utils.convert.convert import FORMAT


def from_static(graph: Union[TemporalGraph, StaticGraph]) -> TemporalGraph:
    """ Returns :class:`~networkx_temporal.classes.TemporalGraph` from a NetworkX graph.

    If the input graph is already a temporal graph, it is added to a new temporal graph object.
    If the input graph is a static graph, it is added to a new temporal graph as a single snapshot.

    .. seealso::

        The `Convert and transform → Graph representations
        <../examples/convert.html#graph-representations>`__
        page for details and examples.

    :param graph: NetworkX graph object.
    """
    if not is_static_graph(graph) and not is_temporal_graph(graph):
        raise TypeError(f"Input must be a valid NetworkX graph, received: {type(graph)}.")
    from .. import empty_graph
    directed = graph.is_directed()
    multigraph = graph.is_multigraph()
    TG = empty_graph(directed=directed, multigraph=multigraph)
    TG.add_snapshot(graph) if is_static_graph(graph) else TG.add_snapshots_from(graph)
    return TG


def to_static(
    graph: Union[TemporalGraph, StaticGraph],
    to: Optional[FORMAT] = None,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    index: Optional[str] = None,
) -> StaticGraph:
    """ Returns a static graph object.

    A static graph is a single object that contains all the nodes and edges of
    the temporal graph. If ``directed`` and ``multigraph`` are unset, the
    returned graph type will match that of the temporal graph. Specifying ``attr``
    allows to store the time of interaction as an edge attribute.

    .. attention::

        As each node in a static graph is unique, dynamic node attributes are not preserved.

    .. seealso::

        The :func:`~networkx_temporal.classes.TemporalGraph.to_unrolled` method for a static
        representation allowing dynamic node attributes.

    :param TemporalGraph graph: Temporal graph object.
    :param str to: Package name or alias to convert the graph object. Optional.
    :param directed: If ``True``, returns a `DiGraph
        <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__.
        Optional.
    :param multigraph: If ``True``, returns a `MultiGraph
        <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__.
        Optional.
    :param index: Edge attribute to store snapshot index. Optional.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    if index is not None and type(index) != str:
        raise TypeError("Argument `index` expects a string.")

    if is_static_graph(graph):
        return convert(graph, to) if to else graph
    if len(graph) == 1:
        return convert(graph[0], to) if to else graph[0]

    if directed is None:
        directed = graph.is_directed()
    if multigraph is None:
        multigraph = graph.is_multigraph()

    G = getattr(nx, f"{'Multi' if multigraph else ''}{f'Di' if directed else ''}Graph")()

    list(G.add_nodes_from(nodes)
         for nodes in graph.nodes(data=True))

    list(G.add_edges_from(
         [(e[0], e[1], {**e[2], **({index: t} if index else {})}) for e in edges])
         for t, edges in enumerate(graph.edges(data=True)))

    G.graph.update(graph.graph)
    return convert(G, to) if to else G
