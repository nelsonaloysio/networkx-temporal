from typing import Any, List, Optional, Union

import networkx as nx

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def get_node_attributes(
    graph: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = None,
    index: bool = True,
) -> List[Any]:
    """ Returns node attribute values for each snapshot and node in the graph.

    For temporal graphs, returns a list of dictionaries, one per snapshot, where keys are nodes
    and values are attribute values. If ``index=False``, returns a list of lists of attribute
    values for each snapshot, where the order of values corresponds to the node order in the graph.

    Note that nodes with missing attributes are skipped by default, unless ``default`` is set.

    .. rubric:: Examples

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(multigraph=False)
        >>>
        >>> TG.add_node("a", group=0)
        >>> TG.add_node("b", group=1)
        >>> TG.add_node("c")
        >>>
        >>> tx.get_node_attributes(TG, attr="group")

        [{'a': 0, 'b': 1}]

    .. code-block:: python

        >>> tx.get_node_attributes(TG, attr="group", default="unknown", index=None)

        [[0, 1, 'unknown']]

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with nodes as keys.
    """
    if is_static_graph(graph):
        node_attrs = nx.get_node_attributes(graph, attr, default=default)
        if not index:
            node_attrs = list(node_attrs.values())
    else:
        node_attrs = [nx.get_node_attributes(G, attr, default=default) for G in graph]
        if not index:
            node_attrs = [list(attrs.values()) for attrs in node_attrs]
    return node_attrs


def get_unique_node_attributes(
    graph: Union[TemporalGraph, StaticGraph], attr: str, default: Any = None) -> List[Any]:
    """ Returns unique node attribute values in graph.

    Note that nodes with missing attributes are skipped by default, unless ``default`` is set.

    .. rubric:: Examples

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(t=2, multigraph=False)
        >>>
        >>> TG.add_node("a", group=0)
        >>> TG.add_node("b", group=1)
        >>> TG.add_node("c")
        >>>
        >>> tx.get_unique_node_attributes(TG, attr="group")

        [0, 1]

    .. code-block:: python

        >>> tx.get_unique_node_attributes(TG, attr="group", default="unknown")

        [[0, 'unknown', 1]]

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The node attribute key.
    :param default: The default value to return if the attribute is not found.
    """
    if not is_temporal_graph(graph) and not is_static_graph(graph):
        raise TypeError("Input expects a temporal or static NetworkX graph object.")

    values = set()
    for g in (graph if is_temporal_graph(graph) else [graph]):
        values.update(nx.get_node_attributes(g, attr, default=default).values())
    return list(values)


def map_attr_to_nodes(
    graph: Union[TemporalGraph, StaticGraph],
    attr: Union[str, dict, list],
    default: Any = None,
    index: bool = True,
) -> list:
    """ Returns a mapping of nodes to attributes. Does not change the graph structure.

    Accepts the following formats for the ``attr`` argument:

    - ``str``: the edge attribute key to extract from the graph.
    - ``dict``: a mapping of nodes to attribute values.
    - ``list``: a list of attribute values corresponding to the nodes in the graph.
    - ``list`` of ``dict``: a list of edge-to-attribute mappings for each snapshot.
    - ``list`` of ``list``: a list of lists of attribute values for each snapshot.

    The output is a list of dictionaries (if ``index=True``) or lists (if ``index=False``)
    mapping nodes to attributes for each snapshot, similar to
    :func:`~networkx_temporal.utils.node.get_node_attributes`.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key, list, or dictionary mapping nodes to attributes.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with nodes as keys.
    """
    if attr is None:
        raise ValueError("Argument `attr` must be provided.")
    if type(attr) not in (str, dict) and type(next(iter(attr))) is not dict:
        if is_static_graph(graph) and len(attr) != graph.order():
            raise ValueError("For static graphs, `attr` length must match number of nodes.")
        if is_temporal_graph(graph) and len(attr) != len(graph):
            raise ValueError("For temporal graphs, `attr` length must match number of snapshots.")
        if is_temporal_graph(graph) and any(len(a) != len(G) for G, a in zip(graph, attr)):
            raise ValueError("For temporal graphs, elements in `attr` must match number of nodes.")

    if type(attr) == str:
        attr_values = [nx.get_node_attributes(G, attr, default=default)
                       for G in ([graph] if is_static_graph(graph) else graph)]
    elif type(attr) == dict:
        attr_values = [{node: attr.get(node, default)
                        for node in (G.nodes() if default is not None else list(attr))}
                       for G in ([graph] if is_static_graph(graph) else graph)]
    elif type(next(iter(attr))) == dict:  # list of dicts
        attr_values = [{node: attr.get(node, default)
                        for node in (G.nodes() if default is not None else list(attr))}
                       for G, attr in zip(graph, attr)]
    elif type(next(iter(attr))) == list:  # list of lists
        attr_values = [{node: attr[i] for i, node in enumerate(G.nodes())}
                       for G, attr in zip(graph, attr)]
    else:  # list of values
        attr_values = [{node: attr[i] for i, node in enumerate(G.nodes())}
                       for G in ([graph] if is_static_graph(graph) else graph)]

    if not index:
        attr_values = [list(attr_values.values()) for attr_values in attr_values]

    return attr_values[0] if is_static_graph(graph) else attr_values


def map_node_attr_to_edges(
    graph: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = None,
    origin: Literal["source", "target", "both"] = "source",
    unique: bool = False,
) -> list:
    """ Returns edge attributes from node attributes.

    For temporal graphs, returns a list of lists, one per snapshot,
    where each list contains the source or target node attribute value for each edge.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(multigraph=False)
        >>>
        >>> TG.add_node("a", group=0)
        >>> TG.add_node("b", group=1)
        >>> TG.add_node("c")
        >>>
        >>> TG.add_edge("a", "b", time=0)
        >>> TG.add_edge("b", "c", time=1)
        >>>
        >>> tx.map_node_attr_to_edges(TG, attr="group", default="unknown")

        [{('a', 'b'): {'group': 0}, ('b', 'c'): {'group': 1}}]

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key to aggregate.
    :param default: The default value to return if the attribute is not found.
    :param origin: Whether to extract attributes from the ``'source'`` or ``'target'``
        node of each edge. If ``'both'``, returns a list with both source and target
        attributes for each edge.
    """
    if type(attr) != str:
        raise TypeError(f"Argument `attr` must be a string, received: {type(attr)}.")
    if origin is not None and origin not in ("source", "target", "both"):
        raise ValueError(f"Argument `origin` must be one of ('source', 'target', 'both').")

    edge_attr = [{} for _ in ([graph] if is_static_graph(graph) else graph)]

    for t, G in enumerate([graph] if is_static_graph(graph) else graph):
        for edge in G.edges():
            u, v = edge[0], edge[1]

            if origin == "source":
                value = G.nodes[u].get(attr, default)
                if value is not None:
                    edge_attr[t][edge] = value

            elif origin == "target":
                value = G.nodes[v].get(attr, default)
                if value is not None:
                    edge_attr[t][edge] = value

            elif origin == "both":
                values = (G.nodes[u].get(attr, default),
                          G.nodes[v].get(attr, default))
                if unique:
                    values = tuple(set(values))
                edge_attr[t][edge] = values

    return edge_attr[0] if is_static_graph(graph) else edge_attr


def map_partitions_to_nodes(
    partitions, nodelist: Optional[list] = None, default: Any = None) -> dict:
    """Returns the mapping of nodes to partition indices.

    :param partitions: List of lists of nodes representing the communities.
    :param nodelist: List of nodes to include in the output mapping. Optional.
    :param default: The default value to return if the node is not found in any partition.
    """
    node_attr = {n: i for i, nodes in enumerate(partitions) for n in nodes}
    if nodelist:
        return {n: node_attr.get(n, default) for n in nodelist
                if default is not None or n in node_attr}
    return node_attr


def partition_nodes(
    graph: Union[TemporalGraph, StaticGraph],
    attr: Union[str, list, dict],
    default: Any = None,
    index: bool = True,
    unique: bool = True,
) -> list:
    """ Returns lists of nodes sharing attribute values.

    This function returns a dictionary or list of dictionaries (one per snapshot) in case of
    temporal graphs, where each key is an attribute and values are the corresponding nodes.

    Note that nodes with missing attributes are skipped by default, unless ``default`` is set.

    .. rubric:: Example

    .. code-block:: python

        >>> TG = tx.temporal_graph()
        >>>
        >>> TG.add_node("a", group=0)
        >>> TG.add_node("b", group=1)
        >>> TG.add_node("c")
        >>>
        >>> tx.partition_nodes(TG, "group")

        [{0: {'a'}, 1: {'b'}}]

    .. code-block:: python

        >>> tx.partition_nodes(TG, "group", default="unknown")

        [{0: {'a'}, 1: {'b'}, 'unknown': {'c'}}]

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: Dictionary, list, or node attribute key for patitioning.
        Passing a sequence of lists or dictionaries is accepted for temporal graphs.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with nodes as keys.
    :param unique: Whether nodes may figure more than once in each set.
    """
    attr_values = map_attr_to_nodes(
        [graph] if is_static_graph(graph) else graph,
        attr,
        default=default,
    )
    partitions = []
    for i, assignments in enumerate(attr_values):
        partitions.append({})
        for node, label in (
            assignments.items() if type(assignments) == dict else enumerate(assignments)
        ):
            if label not in partitions[i]:
                partitions[i][label] = set() if unique else []
            partitions[i][label].add(node) if unique else partitions[i][label].append(node)
    if not index:
        partitions = [[list(values) for values in partition.values()]
                      for partition in partitions]

    return partitions[0] if is_static_graph(graph) else partitions
