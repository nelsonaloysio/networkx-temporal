from typing import Optional

import networkx as nx

from .snapshots import from_snapshots
from ..convert import convert, FORMATS


def from_static(G: nx.Graph) -> dict:
    """
    Returns temporal graph from a static graph.

    :param G: NetworkX graph.
    """
    return from_snapshots([G])


def to_static(
    self,
    to: Optional[FORMATS] = None,
    attr: Optional[str] = None,
    multigraph: bool = True
):
    """
    Returns a static graph from temporal graph.

    A static graph is a single graph that contains all the nodes and edges of
    the temporal graph. If `multigraph` is True, multiple edges among the same
    pair of nodes among snapshots are preserved (default). The time of the
    event can be stored as an edge attribute if `attr` is specified.

    **Note**: as each node in a static graph is unique, dynamic node attributes
    from a temporal graph are not preserved in the static version; to preserve
    dynamic node attributes in a single graph, see the `to_unified` method.

    :param to: Format to convert the static graph to (optional).
    :param attr: Edge attribute name to store time (optional).
    :param multigraph: If True, returns a multigraph (default).
    """
    assert attr not in next(iter(self[0].edges(data=True)))[-1],\
        f"Edge attribute '{attr}' already exists in graph."

    if len(self) == 1:
        return convert(self[0], to) if to else self[0]

    G = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if self.is_directed() else ''}Graph")()

    list(G.add_nodes_from(nodes)
         for nodes in self.nodes(data=True))

    list(G.add_edges_from(
         [(e[0], e[1], {**e[2], **({attr: t} if attr else {})}) for e in edges])
         for t, edges in enumerate(self.edges(data=True)))

    G.name = self.name
    return convert(G, to) if to else G
