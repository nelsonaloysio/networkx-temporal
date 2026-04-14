from typing import Any, List, Optional, Union

import networkx as nx
from networkx import NetworkXError

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def get_edge_attributes(
    TG: TemporalGraph,
    attr: str,
    default: Any = float("nan"),
    index: bool = True,
) -> List[Any]:
    """ Returns attributes of edges in each snapshot.

    .. rubric:: Examples

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(multigraph=False)
        >>>
        >>> TG.add_edge("a", "b", time=0)
        >>> TG.add_edge("b", "c", time=1)
        >>>
        >>> tx.get_edge_attributes(TG, attr="time")

        [{('a', 'b'): 0, ('b', 'c'): 1}]

    .. code-block:: python

        >>> tx.get_edge_attributes(TG, attr="time", index=False)

        [[0, 1]]

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The edge attribute key.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    :param index: Whether to return a dictionary with edges as keys.
    """
    if is_static_graph(TG):
        edge_attr = nx.get_edge_attributes(TG, attr, default=default)
        if not index:
            edge_attr = list(edge_attr.values())
    else:
        edge_attr = [nx.get_edge_attributes(G, attr, default=default) for G in TG]
        if not index:
            edge_attr = [list(attrs.values()) for attrs in edge_attr]

    return edge_attr


def get_unique_edge_attributes(
    TG: TemporalGraph,
    attr: str,
    default: Any = float("nan"),
) -> List[Any]:
    """ Returns unique edge attribute values in graph.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(t=2, multigraph=False)
        >>>
        >>> TG[0].add_edge("a", "b", time=0)
        >>> TG[1].add_edge("b", "c", time=1)
        >>>
        >>> tx.get_unique_edge_attributes(TG, attr="time")

        [0, 1]

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    :param attr: The edge attribute key.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")

    values = set()
    for G in TG:
        values.update(nx.get_edge_attributes(G, attr, default=default).values())
    return list(values)


def map_attr_to_edges(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, dict, list] = None,
    default: Any = float("nan"),
    index: bool = True,
) -> list:
    """ Returns a mapping of edges to attributes. Does not change the graph structure.

    Accepts the following formats for the ``attr`` argument:

    - ``str``: the edge attribute key to extract from the graph.
    - ``dict``: a mapping of edges to attribute values.
    - ``list``: a list of attribute values corresponding to the edges in the graph.
    - ``list`` of ``dict``: a list of edge-to-attribute mappings for each snapshot.
    - ``list`` of ``list``: a list of lists of attribute values for each snapshot.

    The output is a list of dictionaries (if ``index=True``) or lists (if ``index=False``)
    mapping edges to attributes for each snapshot, similar to
    :func:`~networkx_temporal.utils.get_edge_attributes`.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
    :param attr: The edge attribute key, list, or dictionary mapping edges to attributes.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
    :param index: Whether to return a dictionary with edges as keys.
    """
    if attr is None:
        raise ValueError("Argument `attr` must be provided.")
    if type(attr) not in (str, dict):
        if is_static_graph(TG) and len(attr) != TG.order():
            raise ValueError("For static graphs, `attr` length must match number of edges.")
        if is_temporal_graph(TG) and len(attr) != len(TG):
            raise ValueError("For temporal graphs, `attr` length must match number of snapshots.")
        if is_temporal_graph(TG) and any(len(a) != len(G) for G, a in zip(TG, attr)):
            raise ValueError("For temporal graphs, elements in `attr` must match number of edges.")

    if type(attr) == str:
        if TG is None:
            raise ValueError("Argument `TG` must be provided when `attr` is a string.")
        attr_values = [nx.get_edge_attributes(G, attr, default=default)
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(attr) == dict:
        attr_values = [{edge: attr.get(edge, default)
                        for edge in G.edges() if default is not None or edge in attr}
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(next(iter(attr))) == dict:  # list of dicts
        attr_values = [{edge: attr.get(edge, default)
                        for edge in G.edges() if default is not None or edge in attr}
                       for G, attr in zip(TG, attr)]
    elif type(next(iter(attr))) == list:  # list of lists
        attr_values = [{edge: attr[i]
                        for i, edge in enumerate(G.edges()) if default is not None or edge in attr}
                       for G, attr in zip(TG, attr)]
    else:  # list of values
        attr_values = [{edge: attr[i] for i, edge in enumerate(G.edges())}
                       for G in ([TG] if is_static_graph(TG) else TG)]

    if not index:
        attr_values = [list(attr_values.values()) for attr_values in attr_values]

    return attr_values[0] if is_static_graph(TG) else attr_values


def map_edge_attr_to_nodes(
    TG: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = float("nan"),
    unique: bool = False,
) -> list:
    """ Returns node attributes from edge attributes.

    For temporal graphs, returns a list of dictionaries, one per snapshot, where
    each dictionary contains the aggregated edge attribute values for each node.

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
        >>> tx.map_edge_attr_to_nodes(TG, "time")

        [{'a': [0], 'b': [0, 1], 'c': [1]}]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The edge attribute key to aggregate.
    :param unique: Whether to discard duplicate attribute values.
        Default is ``False``.
    """
    if type(attr) != str:
        raise TypeError(f"Argument `attr` must be a string, received: {type(attr)}.")

    if unique:
        node_attr = [{node: set() for node in G.nodes()}
                     for G in ([TG] if is_static_graph(TG) else TG)]

        for t, G in enumerate([TG] if is_static_graph(TG) else TG):
            for u, v, x in G.edges(data=attr, default=default):
                if x is not None:
                    node_attr[t][u].add(x)
                    node_attr[t][v].add(x)
            node_attr[t] = {node: list(attrs) for node, attrs in node_attr[t].items()}

    else:
        node_attr = [{node: [] for node in G.nodes()}
                     for G in ([TG] if is_static_graph(TG) else TG)]

        for t, G in enumerate([TG] if is_static_graph(TG) else TG):
            for u, v, x in G.edges(data=attr, default=default):
                if x is not None:
                    node_attr[t][u].append(x)
                    node_attr[t][v].append(x)

    return node_attr[0] if is_static_graph(TG) else node_attr


def map_partitions_to_edges(partitions, edgelist: list = None):
    """Returns the mapping of edges to partition indices.

    :param partitions: List of lists of edges representing the communities.
    :param edgelist: List of edges to include in the output mapping. Optional.
    """
    edge_attr = {e: i for i, edges in enumerate(partitions) for e in edges}
    if edgelist:
        return {e: edge_attr.get(e, None) for e in edgelist}
    return edge_attr


def partition_edges(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, list, dict] = None,
    default: Any = float("nan"),
    index: bool = True,
    unique: bool = False,
) -> list:
    """ Returns lists of edges sharing attribute values.

    This function returns a dictionary or list of dictionaries (one per snapshot) in case of
    temporal graphs, where each key is an attribute and values are the corresponding edges.
    By default, edges and edges with missing attributes are assigned a ``float('nan')``;
    if ``default=None`` is set instead, edges and edges with missing attributes are skipped.

    .. rubric:: Example

    .. code-block:: python

        >>> TG = tx.temporal_graph()
        >>>
        >>> TG.add_edge("a", "b", time=0)
        >>> TG.add_edge("b", "c", time=1)
        >>>
        >>> TG = TG.slice(attr="time")
        >>> print(TG)
        >>>
        >>> tx.partition_edges(TG, "time")

        {0: {('a', 'b')}, 1: {('b', 'c')}}

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object. Required if ``atr`` is a string.
    :param attr: Dictionary, list, or edge attribute key for patitioning.
        Passing a sequence of lists or dictionaries is accepted for temporal graphs.
    :param default: The default value to return if the attribute is not found.
        If unset, ``float('nan')`` is returned for missing attributes. Passing
        ``None`` (explicitly) will skip edges with missing attributes.
    :param index: Whether to return a dictionary with edges as keys.
    :param unique: Whether edges may figure more than once in each set.
    """
    attr_values = map_attr_to_edges([TG] if is_static_graph(TG) else TG, attr, default=default)

    partitions = []
    for i, assignments in enumerate(attr_values):
        partitions.append({})
        for edge, label in (
            assignments.items() if type(assignments) == dict else enumerate(assignments)
        ):
            if label not in partitions[i]:
                partitions[i][label] = set() if unique else []
            partitions[i][label].add(edge) if unique else partitions[i][label].append(edge)
    if not index:
        partitions = [[list(values) for values in partition.values()]
                      for partition in partitions]

    return partitions[0] if is_static_graph(TG) else partitions
