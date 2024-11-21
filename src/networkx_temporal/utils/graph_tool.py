from typing import Any, Union

import graph_tool as gt
import networkx as nx

INT16, INT32, INT64 = 2**15, 2**31, 2**63

NAME_TYPE = {
    "bytes": "object",
    "dict": "object",
    "str": "string",
}

NUM_TYPE = {
    "short": 0,
    "int": 1,
    "long": 2,
    "double": 3,
    "long double": 4,
}


def nx2gt(nxG: nx.Graph, index: str = "id", encoding: str = "ascii", errors: str = "strict") -> gt.Graph:
    """
    Converts a NetworkX object to a graph-tool object with
    properties and attributes preserved as much as possible.

    Original implementation by `bbengfort (GitHub) <
    https://gist.github.com/bbengfort/a430d460966d64edc6cad71c502d7005>`_.

    :param nxG: NetworkX graph object.
    :param index: Property name to use as the node identifier.
        Default is ``'id'``.
    :param encoding: Encoding to use for string conversion.
        Default is ``'ascii'``.
    :param errors: Error handling scheme for string conversion.
        Default is `'`strict'``.

    :rtype: graph_tool.Graph
    """
    gtG = gt.Graph(directed=nxG.is_directed())

    # Map graph properties.
    for key, value in nxG.graph.items():
        type_, key, value = get_prop(key, value, encoding=encoding, errors=errors)
        gtG.graph_properties[key] = gtG.new_graph_property(type_)
        gtG.graph_properties[key] = value

    # Map node properties.
    vs, vp = {}, {}
    for node, data in nxG.nodes(data=True):
        type_, key, value = get_prop(index, node, encoding=encoding, errors=errors)
        vp[index].add(type_) if index in vp else vp.__setitem__(index, {type_})
        for key, value in data.items():
            type_, key, value  = get_prop(key, value, encoding=encoding, errors=errors)
            vp[key].add(type_) if key in vp else vp.__setitem__(key, {type_})

    # Verify numeric type and ensure each property has a single type.
    for key, types in vp.items():
        types_ = get_types(types)
        assert len(types_) == 1, f"Multiple types for node property '{key}': {types}."
        gtG.vp[key] = gtG.new_vertex_property(types_[0])

    # Add nodes and their properties.
    gtG.vp[index] = gtG.new_vertex_property("string")
    for node, data in nxG.nodes(data=True):
        v = gtG.add_vertex()
        gtG.vp[index][v] = str(node)
        for key, value in data.items():
            gtG.vp[key][v] = value
        vs[node] = v

    # Map edge properties.
    ep = {}
    for src, dst, data in nxG.edges(data=True):
        for key, value in data.items():
            type_, key, value = get_prop(key, value, encoding=encoding, errors=errors)
            ep[key].add(type_) if key in ep else ep.__setitem__(key, {type_})

    # Verify numeric type and ensure each property has a single type.
    for key, types in ep.items():
        types_ = get_types(types)
        assert len(types_) == 1, f"Multiple types for edge property '{key}': {types}."
        gtG.ep[key] = gtG.new_edge_property(types_[0])

    # Add edges and their properties.
    for src, dst, data in nxG.edges(data=True):
        e = gtG.add_edge(vs[src], vs[dst])
        for key, value in data.items():
            gtG.ep[key][e] = value

    return gtG


def get_prop(key: Any, value: Any, encoding: str = "ascii", errors: str = "strict") -> tuple:
    """
    Performs typing and key/value conversion for graph-tool's `PropertyMap` class.

    :param key: Attribute key.
    :param value: Attribute value.
    :param encoding: Encoding to use for string conversion.
        Default is ``'ascii'``.
    :param errors: Error handling scheme for string conversion.
        Default is `'`strict'``.
    """
    key = key.encode(encoding, errors=errors).decode(encoding)
    type_ = type(value).__name__
    type_ = NAME_TYPE.get(type_, type_)

    if type_ in ("int", "float"):
        if -INT16 <= value < INT16:
            type_ = "short"
        elif -INT32 <= value < INT32:
            type_ = "int"
        elif -INT64 <= value < INT64:
            type_ = "long"
        elif len(str(value)) <= 8:
            type_ = "double"
        else:
            type_ = "long double"

    return type_, key, value


def get_types(types: list) -> list:
    """
    Returns the type of a property based on list of observed types.

    :param types: List of types.
    """
    type_ = set(types)

    if all(type_ in NUM_TYPE for type_ in types):
        type_ = [max(types, key=NUM_TYPE.get)]

    return list(type_)
