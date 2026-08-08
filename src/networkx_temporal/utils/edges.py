from typing import Any, List, Optional, Union

import networkx as nx

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def get_edge_attributes(
    graph: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = None,
    index: bool = True,
    values: Optional[Literal["list", "set"]] = None
) -> List[Any]:
    """ Returns edge attribute values for each snapshot and edge in the graph.

    For temporal graphs, returns a list of dictionaries, one per snapshot, where keys are edges
    and values are attribute values. If ``index=False``, returns a list of lists of attribute
    values for each snapshot, where the order of values corresponds to the edge order in the graph.
    If ``values`` is set to ``'list'`` or ``'set'``, returns a list or a set of values per node.

    Note that edges with missing attributes are skipped by default, unless ``default`` is set.

    .. rubric:: Examples

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.temporal_graph(multigraph=False)
        >>>
        >>> TG.add_edge("a", "b", time=0)
        >>> TG.add_edge("b", "c", time=1)
        >>> TG.add_edge("a", "c")
        >>>
        >>> tx.get_edge_attributes(TG, attr="time")

        [{('a', 'b'): 0, ('b', 'c'): 1}]

    .. code-block:: python

        >>> tx.get_edge_attributes(TG, attr="time", default="unknown", index=False)

        [[0, 1, 'unknown']]

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The edge attribute key.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with edges as keys.
        If ``False``, returns a list of attribute values for each snapshot, where the order of
        values corresponds to the edge order in the graph. Default is ``True``.
    :param values: If set, returns a dictionary with a single key-value pair for each edge, being:

       - ``'list'``: returns a list of attribute values per edge across time.

       - ``'set'``: returns a set of unique attribute values per edge across time.
    """
    if is_static_graph(graph):
        edge_attrs = nx.get_edge_attributes(graph, attr, default=default)
        if not index:
            edge_attrs = list(edge_attrs.values())
    else:
        if values is None:
            edge_attrs = [
                nx.get_edge_attributes(G, attr, default=default)
                for G in graph
            ]
        elif values in (list, "list"):
            edge_attrs = {}
            list(
                edge_attrs.setdefault(edge, []).append(value)
                for G in graph
                for edge, value in nx.get_edge_attributes(G, attr, default=default).items()
            )
        elif values in (set, "set"):
            edge_attrs = {}
            list(
                edge_attrs.setdefault(edge, set()).add(value)
                for G in graph
                for edge, value in nx.get_edge_attributes(G, attr, default=default).items()
            )
        else:
            raise ValueError(f"Argument `values` must be `None` or one of: 'list', 'set'.")
        if not index:
            edge_attrs = (
                [list(attrs.values()) for attrs in edge_attrs]
                if values is None else list(edge_attrs.values())
            )
    return edge_attrs


def get_unique_edge_attributes(
    graph: Union[TemporalGraph, StaticGraph], attr: str, default: Any = None) -> List[Any]:
    """ Returns unique edge attribute values in graph.

    Note that edges with missing attributes are skipped by default, unless ``default`` is set.

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

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param default: The default value to return if the attribute is not found.
    :param attr: The edge attribute key.
    """
    if not is_temporal_graph(graph) and not is_static_graph(graph):
        raise TypeError("Input expects a temporal or static NetworkX graph object.")

    values = set()
    for g in (graph if is_temporal_graph(graph) else [graph]):
        values.update(nx.get_edge_attributes(g, attr, default=default).values())
    return list(values)


def map_attr_to_edges(
    graph: Union[TemporalGraph, StaticGraph],
    attr: Union[str, dict, list],
    default: Any = None,
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
    :func:`~networkx_temporal.utils.edge.get_edge_attributes`.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The edge attribute key, list, or dictionary mapping edges to attributes.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with edges as keys.
    """
    if attr is None:
        raise ValueError("Argument `attr` must be provided.")
    if type(attr) not in (str, dict) and type(next(iter(attr))) is not dict:
        if is_static_graph(graph) and len(attr) != graph.size():
            raise ValueError("For static graphs, `attr` length must match number of edges.")
        if is_temporal_graph(graph) and len(attr) != len(graph):
            raise ValueError("For temporal graphs, `attr` length must match number of snapshots.")
        if is_temporal_graph(graph) and any(len(a) != len(G) for G, a in zip(graph, attr)):
            raise ValueError("For temporal graphs, elements in `attr` must match number of edges.")

    if type(attr) == str:
        attr_values = [nx.get_edge_attributes(G, attr, default=default)
                       for G in ([graph] if is_static_graph(graph) else graph)]
    elif type(attr) == dict:
        attr_values = [{edge: attr.get(edge, default)
                        for edge in (G.edges() if default is not None else list(attr))}
                       for G in ([graph] if is_static_graph(graph) else graph)]
    elif type(next(iter(attr))) == dict:  # list of dicts
        attr_values = [{edge: attr.get(edge, default)
                        for edge in (G.edges() if default is not None else list(attr))}
                       for G, attr in zip(graph, attr)]
    elif type(next(iter(attr))) == list:  # list of lists
        attr_values = [{edge: attr[i] for i, edge in enumerate(G.edges())}
                       for G, attr in zip(graph, attr)]
    else:  # list of values
        attr_values = [{edge: attr[i] for i, edge in enumerate(G.edges())}
                       for G in ([graph] if is_static_graph(graph) else graph)]

    if not index:
        attr_values = [list(attr_values.values()) for attr_values in attr_values]

    return attr_values[0] if is_static_graph(graph) else attr_values


def map_edge_attr_to_nodes(
    graph: Union[TemporalGraph, StaticGraph],
    attr: str,
    default: Any = None,
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

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The edge attribute key to aggregate.
    :param default: The default value to return if the attribute is not found.
    :param unique: Whether to discard duplicate attribute values. Default is ``False``.
    """
    if type(attr) != str:
        raise TypeError(f"Argument `attr` must be a string, received: {type(attr)}.")

    if unique:
        node_attr = [{node: set() for node in G.nodes()}
                     for G in ([graph] if is_static_graph(graph) else graph)]

        for t, G in enumerate([graph] if is_static_graph(graph) else graph):
            for u, v, x in G.edges(data=attr, default=default):
                if x is not None:
                    node_attr[t][u].add(x)
                    node_attr[t][v].add(x)
            node_attr[t] = {node: list(attrs) for node, attrs in node_attr[t].items()}

    else:
        node_attr = [{node: [] for node in G.nodes()}
                     for G in ([graph] if is_static_graph(graph) else graph)]

        for t, G in enumerate([graph] if is_static_graph(graph) else graph):
            for u, v, x in G.edges(data=attr, default=default):
                if x is not None:
                    node_attr[t][u].append(x)
                    node_attr[t][v].append(x)

    return node_attr[0] if is_static_graph(graph) else node_attr


def map_partitions_to_edges(
    partitions, edgelist: Optional[list] = None, default: Any = None) -> dict:
    """Returns the mapping of edges to partition indices.

    :param partitions: List of lists of edges representing the communities.
    :param edgelist: List of edges to include in the output mapping. Optional.
    :param default: The default value to return if the edge is not found in any partition.
    """
    edge_attr = {e: i for i, edges in enumerate(partitions) for e in edges}
    if edgelist:
        return {e: edge_attr.get(e, default) for e in edgelist
                if default is not None or e in edge_attr}
    return edge_attr


def partition_edges(
    graph: Union[TemporalGraph, StaticGraph],
    attr: Union[str, list, dict],
    default: Any = None,
    index: bool = True,
    unique: bool = False,
) -> list:
    """ Returns lists of edges sharing attribute values.

    This function returns a dictionary or list of dictionaries (one per snapshot) in case of
    temporal graphs, where each key is an attribute and values are the corresponding edges.

    Note that edges with missing attributes are skipped by default, unless ``default`` is set.

    .. rubric:: Example

    .. code-block:: python

        >>> TG = tx.temporal_graph(multigraph=False)
        >>>
        >>> TG.add_edge("a", "b", time=0)
        >>> TG.add_edge("b", "c", time=1)
        >>>
        >>> TG = TG.slice(attr="time")
        >>> print(TG)
        >>>
        >>> tx.partition_edges(TG, "time")

        {0: {('a', 'b')}, 1: {('b', 'c')}}

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: Dictionary, list, or edge attribute key for patitioning.
        Passing a sequence of lists or dictionaries is accepted for temporal graphs.
    :param default: The default value to return if the attribute is not found.
    :param index: Whether to return a dictionary with edges as keys.
    :param unique: Whether edges may figure more than once in each set.
    """
    attr_values = map_attr_to_edges(
        [graph] if is_static_graph(graph) else graph,
        attr,
        default=default,
    )
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

    return partitions[0] if is_static_graph(graph) else partitions
