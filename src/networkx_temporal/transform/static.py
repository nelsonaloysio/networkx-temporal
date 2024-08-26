from typing import Optional

import networkx as nx

from .snapshots import from_snapshots
from ..convert import convert, FORMATS
from ..typing import TemporalGraph


def from_static(G: nx.Graph) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.TemporalGraph` object from a static graph.

    :param G: NetworkX graph.

    :rtype: TemporalGraph
    """
    return from_snapshots([G])


def to_static(
    self,
    to: Optional[FORMATS] = None,
    attr: Optional[str] = None,
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
) -> nx.Graph:
    """
    Returns a static (flattened) graph.

    A static graph is a single graph that contains all the nodes and edges of
    the temporal graph. If ``directed`` and ``multigraph`` are unset, the
    returned graph type will be the same as the temporal graph. The time of
    the event can be stored as an edge attribute if `attr` is specified.

    .. attention::

        As each node in a static graph is unique, dynamic node attributes are not preserved.

    .. seealso::

        The :func:`~networkx_temporal.to_unified` method allows to preserve dynamic node attributes
        in a single graph.

    :param str to: Package name or alias to convert the graph object
        (see :func:`~networkx_temporal.convert`). Optional.
    :param attr: Edge attribute name to store time. Optional.
    :param directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`_.
        Optional.
    :param multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.
        Optional.
    """
    assert attr is None or sum(self.size()) == 0 or attr not in next(iter(self[0].edges(data=True)))[-1],\
        f"Edge attribute '{attr}' already exists in graph."

    if len(self) == 1:
        return convert(self[0], to) if to else self[0]

    if directed is None:
        directed = self.is_directed()

    if multigraph is None:
        multigraph = self.is_multigraph()

    G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")()

    list(G.add_nodes_from(nodes)
         for nodes in self.nodes(data=True))

    list(G.add_edges_from(
         [(e[0], e[1], {**e[2], **({attr: t} if attr else {})}) for e in edges])
         for t, edges in enumerate(self.edges(data=True)))

    G.name = self.name
    return convert(G, to) if to else G
