from typing import Optional, Union

import networkx as nx

from ..utils import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_snap(
    G: Union[TemporalGraph, StaticGraph, list],
    node_id: Optional[str] = "id",
    node_attrs: Optional[Union[bool, list]] = True,
    edge_attrs: Optional[Union[bool, list]] = True,
):
    """
    Convert from NetworkX to `SNAP <https://snap.stanford.edu/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param node_id: Attribute key to use as node identifier. Optional. Default is ``'id'``.
    :param node_attrs: Boolean or list of node attributes to include in the conversion.
        Optional. Default is ``True``.
    :param edge_attrs: Boolean or list of edge attributes to include in the conversion.
        Optional. Default is ``True``.

    :rtype: snap.TGraph
    """
    import snap

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Input must be a temporal or static NetworkX graph."

    if is_temporal_graph(G) or type(G) == list:
        return [to_snap(H, node_id=node_id, node_attrs=node_attrs, edge_attrs=edge_attrs) for H in G]

    assert type(G) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Input graph must be a static NetworkX graph object, received: {type(G)}."
    assert type(node_id) == str,\
        f"Node identifier must be a string, received: {type(node_id)}."
    assert node_attrs is None or type(node_attrs) in (bool, list),\
        f"Node attributes must be a boolean or list, received: {type(node_attrs)}."
    assert edge_attrs is None or type(edge_attrs) in (bool, list),\
        f"Edge attributes must be a boolean or list, received: {type(edge_attrs)}."
    assert type(node_attrs) != list or node_id not in node_attrs,\
        f"Node identifier ('{node_id}') cannot be included as a node attribute."

    directed = G.is_directed()
    multigraph = G.is_multigraph()

    # Create new graph object.
    if node_id or node_attrs or edge_attrs or multigraph:
        H = snap.TNEANet.New()
    elif directed:
        H = snap.TNGraph.New()
    else:
        H = snap.TUNGraph.New()

    # Obtain node mapping and add nodes to graph.
    nodes = {str(n): i for i, n in enumerate(G.nodes(data=False))}
    list(map(lambda n: H.AddNode(nodes[n]), G.nodes(data=False)))

    # Add edges to graph (and reversed edges if necessary).
    for i, e in enumerate(G.edges(data=False)):
        H.AddEdge(nodes[e[0]], nodes[e[1]], i)

    if not directed and (multigraph or node_attrs or edge_attrs):
        for i, e in enumerate(G.edges(data=False)):
            H.AddEdge(nodes[e[1]], nodes[e[0]], i + G.size())

    # Add node indices.
    if node_id:
        H.AddStrAttrN(node_id)
        for n in nodes:
            H.AddStrAttrDatN(nodes[n], n, node_id)

    # Add node attributes.
    if node_attrs:
        added_node_attrs = set()
        for n in G.nodes(data=node_attrs):
            for k, v in n[-1].items():
                # Add node attribute to the graph.
                if k not in added_node_attrs:
                    if isinstance(v, int):
                        H.AddIntAttrN(k)
                    elif isinstance(v, float):
                        H.AddFltAttrN(k)
                    else:
                        H.AddStrAttrN(k)
                    added_node_attrs.add(k)
                # Add attribute value to the node.
                if isinstance(v, int):
                    H.AddIntAttrDatN(nodes[n], v, k)
                elif isinstance(v, float):
                    H.AddFltAttrDatN(nodes[n], v, k)
                else:
                    H.AddStrAttrDatN(nodes[n], v, k)

    # Add edge attributes.
    if edge_attrs:
        added_edge_attrs = set()
        for i, e in enumerate(G.edges(data=edge_attrs)):
            for k, v in e[-1].items():
                # Add edge attribute to the graph.
                if k not in added_edge_attrs:
                    if isinstance(v, int):
                        H.AddIntAttrE(k)
                    elif isinstance(v, float):
                        H.AddFltAttrE(k)
                    else:
                        H.AddStrAttrE(k)
                        added_edge_attrs.add(k)
                # Add attribute value to the edge.
                if isinstance(v, int):
                    H.AddIntAttrDatE(i, v, k)
                elif isinstance(v, float):
                    H.AddFltAttrDatE(i, v, k)
                else:
                    H.AddStrAttrDatE(i, v, k)
        # Add reversed edge attributes.
        if not directed and (multigraph or node_attrs or edge_attrs):
            for i, e in enumerate(G.edges(data=edge_attrs)):
                if isinstance(v, int):
                    H.AddIntAttrDatE(i + G.size(), v, k)
                elif isinstance(v, float):
                    H.AddFltAttrDatE(i + G.size(), v, k)
                else:
                    H.AddStrAttrDatE(i + G.size(), v, k)

    return H
