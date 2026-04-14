from typing import Any, List, Optional, Union

import networkx as nx
from networkx import NetworkXError

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def get_node_attributes(
    TG: TemporalGraph,
    attr: str,
    default: Any = float("nan"),
    index: bool = True,
) -> List[Any]:
    """ Returns attributes of nodes in each snapshot.

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

        [{'a': 0, 'b': 1, 'c': nan}]

    .. code-block:: python

        >>> tx.get_node_attributes(TG, attr="group", default=None, index=None)

        [[0, 1]]

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The node attribute key.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    :param index: Whether to return a dictionary with nodes as keys.
    """
    if is_static_graph(TG):
        node_attrs = nx.get_node_attributes(TG, attr, default=default)
        if not index:
            node_attrs = list(node_attrs.values())
    else:
        node_attrs = [nx.get_node_attributes(G, attr, default=default) for G in TG]
        if not index:
            node_attrs = [list(attrs.values()) for attrs in node_attrs]
    return node_attrs


def get_unique_node_attributes(
    TG: TemporalGraph,
    attr: str,
    default: Any = float("nan"),
) -> List[Any]:
    """ Returns unique node attribute values in graph.

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

        [0, 1, nan]

    .. code-block:: python

        >>> tx.get_unique_node_attributes(TG, attr="group", default="unknown")

        [0, 1, 'unknown']

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The node attribute key.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")

    values = set()
    for G in TG:
        values.update(nx.get_node_attributes(G, attr, default=default).values())
    return list(values)


def map_attr_to_nodes(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, dict, list] = None,
    default: Any = float("nan"),
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

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key, list, or dictionary mapping nodes to attributes.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    :param index: Whether to return a dictionary with nodes as keys.
    """
    if attr is None:
        raise ValueError("Argument `attr` must be provided.")
    if type(attr) not in (str, dict):
        if is_static_graph(TG) and len(attr) != TG.order():
            raise ValueError("For static graphs, `attr` length must match number of nodes.")
        if is_temporal_graph(TG) and len(attr) != len(TG):
            raise ValueError("For temporal graphs, `attr` length must match number of snapshots.")
        if is_temporal_graph(TG) and any(len(a) != len(G) for G, a in zip(TG, attr)):
            raise ValueError("For temporal graphs, elements in `attr` must match number of nodes.")

    if type(attr) == str:
        if TG is None:
            raise ValueError("Argument `TG` must be provided when `attr` is a string.")
        attr_values = [nx.get_node_attributes(G, attr, default=default)
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(attr) == dict:
        attr_values = [{node: attr.get(node, default)
                        for node in G.nodes() if default is not None or node in attr}
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(next(iter(attr))) == dict:  # list of dicts
        attr_values = [{node: attr.get(node, default)
                        for node in G.nodes() if default is not None or node in attr}
                       for G, attr in zip(TG, attr)]
    elif type(next(iter(attr))) == list:  # list of lists
        attr_values = [{node: attr[i]
                        for i, node in enumerate(G.nodes()) if default is not None or node in attr}
                       for G, attr in zip(TG, attr)]
    else:  # list of values
        attr_values = [{node: attr[i] for i, node in enumerate(G.nodes())}
                       for G in ([TG] if is_static_graph(TG) else TG)]

    if not index:
        attr_values = [list(attr_values.values()) for attr_values in attr_values]

    return attr_values[0] if is_static_graph(TG) else attr_values


def map_node_attr_to_edges(
    TG: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = float("nan"),
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

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key to aggregate.
    :param default: The default value to return if the attribute is not found.
        If unset, ``float('nan')`` is returned for missing attributes. Passing
        ``None`` (explicitly) will skip edges with missing attributes.
    :param origin: Whether to extract attributes from the ``'source'`` or ``'target'``
        node of each edge. If ``'both'``, returns a list with both source and target
        attributes for each edge.
    """
    if type(attr) != str:
        raise TypeError(f"Argument `attr` must be a string, received: {type(attr)}.")
    if origin is not None and origin not in ("source", "target", "both"):
        raise ValueError(f"Argument `origin` must be one of ('source', 'target', 'both').")

    edge_attr = [{} for _ in ([TG] if is_static_graph(TG) else TG)]

    for t, G in enumerate([TG] if is_static_graph(TG) else TG):
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

    return edge_attr[0] if is_static_graph(TG) else edge_attr


def map_partitions_to_nodes(partitions, nodelist: list = None):
    """Returns the mapping of nodes to partition indices.

    :param partitions: List of lists of nodes representing the communities.
    :param nodelist: List of nodes to include in the output mapping. Optional.
    """
    node_attr = {n: i for i, nodes in enumerate(partitions) for n in nodes}
    if nodelist:
        return {n: node_attr.get(n, None) for n in nodelist}
    return node_attr


def partition_nodes(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, list, dict] = None,
    default: Any = float("nan"),
    index: bool = True,
    unique: bool = True,
) -> list:
    """ Returns lists of nodes sharing attribute values.

    This function returns a dictionary or list of dictionaries (one per snapshot) in case of
    temporal graphs, where each key is an attribute and values are the corresponding nodes.
    By default, nodes and edges with missing attributes are assigned a ``float('nan')``;
    if ``default=None`` is set instead, nodes and edges with missing attributes are skipped.

    .. rubric:: Example

    .. code-block:: python

        >>> TG = tx.temporal_graph()
        >>>
        >>> TG.add_node("a", group=0)
        >>> TG.add_node("b", group=1)
        >>> TG.add_node("c")
        >>>
        >>> tx.partition_nodes(TG, "group")

        {0: {'a'}, 1: {'b'}, nan: {'c'}}

    .. code-block:: python

        >>> tx.partition_nodes(TG, "group", default=None)

        {0: {'a'}, 1: {'b'}}

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object. Required if ``atr`` is a string.
    :param attr: Dictionary, list, or node attribute key for patitioning.
        Passing a sequence of lists or dictionaries is accepted for temporal graphs.
    :param default: The default value to return if the attribute is not found.
        If unset, ``float('nan')`` is returned for missing attributes. Passing
        ``None`` (explicitly) will skip nodes with missing attributes.
    :param index: Whether to return a dictionary with nodes as keys.
    :param unique: Whether nodes may figure more than once in each set.
    """
    attr_values = map_attr_to_nodes([TG] if is_static_graph(TG) else TG, attr, default=default)

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

    return partitions[0] if is_static_graph(TG) else partitions


