from typing import Any

import networkx as nx

import graph_tool as gt

TYPE_NAME = {
    "dict": "object",
    "str": "string"
}


def get_prop_type(value: Any, key=None, encoding: str = "ascii", errors: str = "strict") -> tuple:
    """
    Performs typing and value conversion for the graph_tool PropertyMap class.
    If a key is provided, it also ensures the key is in a format that can be
    used with the PropertyMap. Returns a 3-tuple, (type_name, value, key).
    """
    if type(value) == int:
        value = float(value)
    elif type(value) == str:
        value = value.encode(encoding, errors=errors)
    elif type(value) == bytes:
        value = value.decode(encoding, errors=errors)

    key = key.encode(encoding, errors=errors).decode(encoding)
    type_name = type(value).__name__
    type_name = TYPE_NAME.get(type_name, type_name)
    return type_name, value, key


def nx2gt(nxG: nx.Graph, encoding: str = "ascii", errors: str = "strict"):
    """
    Converts a NetworkX graph to a graph-tool graph.

    Original implementation:
    https://gist.github.com/ioctls/8bef992707006969510e33c20a0d42b6
    """
    gtG = gt.Graph(directed=nxG.is_directed())
    nprops, eprops = set(), set()

    # Add the Graph properties as "internal properties".
    for key, value in nxG.graph.items():
        type_name, value, key = get_prop_type(value, key, encoding=encoding, errors=errors)
        prop = gtG.new_graph_property(type_name)
        gtG.graph_properties[key] = prop
        gtG.graph_properties[key] = value

    # Add node property map.
    for node, data in nxG.nodes(data=True):
        for key, val in data.items():
            if key in nprops:
                continue
            type_name, _, key  = get_prop_type(val, key, encoding=encoding, errors=errors)
            prop = gtG.new_vertex_property(type_name)
            gtG.vertex_properties[key] = prop
            nprops.add(key)

    # Also add the node id: in NetworkX a node can be any hashable type, but
    # in graph-tool node are defined as indices. So we capture any strings
    # in a special PropertyMap called "id" -- modify as needed!
    gtG.vertex_properties["id"] = gtG.new_vertex_property("string")

    # Add edge property map.
    for src, dst, data in nxG.edges(data=True):
        for key, val in data.items():
            if key in eprops:
                continue
            type_name, _, key = get_prop_type(val, key, encoding=encoding, errors=errors)
            prop = gtG.new_edge_property(type_name)
            gtG.edge_properties[key] = prop
            eprops.add(key)

    # Add nodes and their properties.
    vertices = {} # vertex mapping for tracking edges later
    for node, data in nxG.nodes(data=True):
        # Create the vertex and annotate for our edges later.
        v = gtG.add_vertex()
        vertices[node] = v
        # Set the vertex properties (vp), including id.
        data["id"] = str(node)
        for key, value in data.items():
            gtG.vp[key][v] = value

    # Add edges and their properties.
    for src, dst, data in nxG.edges(data=True):
        # Look up the vertex structs from our vertices mapping and add edge.
        e = gtG.add_edge(vertices[src], vertices[dst])
        # Add the edge properties (ep).
        for key, value in data.items():
            gtG.ep[key][e] = value

    return gtG
