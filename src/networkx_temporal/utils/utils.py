from typing import Any, List, Optional, Union

import networkx as nx
from networkx import NetworkXError

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def combine_snapshots(graphs: List[TemporalGraph]) -> TemporalGraph:
    """ Returns temporal graph with combined snapshots.

    Each snapshot in the resulting temporal graph is the union of the corresponding
    snapshots at each index :math:`t` from ``graphs``. All input temporal graphs
    must have the same number of snapshots.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG1 = tx.temporal_graph()
        >>> TG2 = tx.temporal_graph()
        >>>
        >>> TG1.add_edge("a", "b")
        >>> TG2.add_edge("c", "b")
        >>>
        >>> TG = tx.combine_snapshots([TG1, TG2])
        >>> print(TG)

    :param object graphs: A list of :class:`~networkx_temporal.classes.TemporalGraph`
        objects.
    """
    if type(graphs) != list:
        raise TypeError(f"Argument `graphs` must be a list, received: {type(graphs)}.")
    if len(graphs) == 0:
        raise ValueError("Argument `graphs` must contain at least one graph.")

    temporal = all(is_temporal_graph(G) for G in graphs)
    if not temporal:
        raise NetworkXError("All inputs must be temporal NetworkX graphs.")

    multigraph = all(G.is_multigraph() == graphs[0].is_multigraph() for G in graphs)
    if not multigraph:
        raise NetworkXError("All inputs must be either multigraph or non-multigraph objects.")

    if any(len(G) != len(graphs[0]) for G in graphs):
        raise ValueError("All temporal graphs must have the same number of snapshots.")

    # Initialize empty temporal graph of the same type.
    TG = graphs[0].__class__(t=0)

    TG.add_snapshots_from([
        nx.compose_all([TG[t] for TG in graphs]) for t in range(len(graphs[0]))
    ])

    return TG


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
        return nx.get_edge_attributes(TG, attr, default=default)
    edge_attr = [nx.get_edge_attributes(G, attr, default=default) for G in TG]
    if not index:
        edge_attr = [list(edge_attr.values()) for edge_attr in edge_attr]
    return edge_attr


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
        return nx.get_node_attributes(TG, attr, default=default)
    node_attr = [nx.get_node_attributes(G, attr, default=default) for G in TG]
    if not index:
        node_attr = [list(node_attr.values()) for node_attr in node_attr]
    return node_attr


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


def get_unique_node_attributes(
    TG: TemporalGraph,
    attr: str,
    default: Any = float("nan"),
) -> List[Any]:
    """ Returns unique node attribute values in graph.

    .. rubric:: Example

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

        [0]

    .. code-block:: python

        >>> tx.get_unique_node_attributes(TG, attr="group", default="unknown")

        [0, "unknown"]

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


def map_attr_to_edges(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, dict, list] = None,
    default: Any = float("nan"),
    index: bool = True,
) -> list:
    """ Maps attributes to edges in each snapshot.

    This function maps attributes to edges in either a static or temporal graph and
    is similar to :func:`~networkx_temporal.classes.TemporalGraph.get_node_attributes`.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
    :param attr: The node attribute key, list, or dictionary mapping nodes to attributes.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
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
        attr_values = [nx.get_edge_attributes(G, attr, default=default)
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(attr) == dict:
        attr_values = [{edge: attr.get(edge, default)
                        for edge in G.edges() if default is not None or edge in attr}
                       for G in ([TG] if is_static_graph(TG) else TG)]
    elif type(next(iter(attr))) == type(attr):
        attr_values = [{edge: attr[i]
                        for i, edge in enumerate(G.edges()) if default is not None or edge in attr}
                       for attr, G in zip(attr, TG)]
    elif type(next(iter(attr))) == type(attr):
        attr_values = [{edge: attr.get(edge, default)
                        for edge in G.edges() if default is not None or edge in attr}
                       for attr, G in zip(attr, TG)]
    else:
        attr_values = [{edge: attr[i] for i, edge in enumerate(G.edges())}
                       for G in ([TG] if is_static_graph(TG) else TG)]

    if not index:
        attr_values = [list(attr_values.values()) for attr_values in attr_values]

    return attr_values[0] if is_static_graph(TG) else attr_values


def map_attr_to_nodes(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, dict, list] = None,
    default: Any = float("nan"),
    index: bool = True,
) -> list:
    """ Maps attributes to nodes in each snapshot.

    This function maps attributes to nodes in either a static or temporal graph and
    is similar to :func:`~networkx_temporal.classes.TemporalGraph.get_node_attributes`.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: The node attribute key, list, or dictionary mapping nodes to attributes.
    :param default: The default value to return if the attribute is not found.
        Returns ``float('nan')`` if unset.
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
    elif type(next(iter(attr))) == dict:
        attr_values = [{node: attr.get(node, default)
                        for node in G.nodes() if default is not None or node in attr}
                       for attr, G in zip(attr, TG)]
    elif type(next(iter(attr))) == type(attr):
        attr_values = [{node: attr[i]
                        for i, node in enumerate(G.nodes()) if default is not None or node in attr}
                       for attr, G in zip(attr, TG)]
    else:
        attr_values = [{node: attr[i] for i, node in enumerate(G.nodes())}
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


def map_partitions_to_edges(partitions, edgelist: list = None):
    """Returns the mapping of edges to partition indices.

    :param partitions: List of lists of edges representing the communities.
    :param edgelist: List of edges to include in the output mapping. Optional.
    """
    edge_attr = {e: i for i, edges in enumerate(partitions) for e in edges}
    if edgelist:
        return {e: edge_attr.get(e, None) for e in edgelist}
    return edge_attr


def map_partitions_to_nodes(partitions, nodelist: list = None):
    """Returns the mapping of nodes to partition indices.

    :param partitions: List of lists of nodes representing the communities.
    :param nodelist: List of nodes to include in the output mapping. Optional.
    """
    node_attr = {n: i for i, nodes in enumerate(partitions) for n in nodes}
    if nodelist:
        return {n: node_attr.get(n, None) for n in nodelist}
    return node_attr


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


def propagate_snapshots(
    TG: TemporalGraph,
    method: Literal["ffill", "bfill"] = "ffill",
    delta: Optional[int] = None,
) -> TemporalGraph:
    """ Propagates nodes and edges across snapshots.

    Returns a temporal graph where nodes and edges are preserved
    among snapshots.

    .. seealso::

        The `Examples → Basic operations → Propagating snapshots
        <../examples/basics.html#propagating-snapshots>`__  page for an example.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: The propagation method. Can be either:

       - ``'ffill'``: propagates nodes and edges forward in time
         (from earlier to later snapshots);

       - ``'bfill'``: propagates nodes and edges backward in time
         (from later to earlier snapshots).
    :param delta: The number of snapshots to propagate over.
        If ``None`` (default), propagates over all snapshots.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")
    if method not in ("ffill", "bfill"):
        raise ValueError("Argument `method` must be one of ('ffill', 'bfill').")

    TG = TG.copy()

    if method == "ffill":
        for t in range(1, len(TG)):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(max(0, t - delta if delta is not None else 0), t + 1)
            ])
    else:  # method == "bfill"
        for t in range(len(TG)-2, -1, -1):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(t, min(len(TG), t + (delta if delta is not None else len(TG))))
            ])

    return TG


def temporal_edge_matrix(
    TG: TemporalGraph,
    method: Literal["jaccard", "union", "intersect", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns matrix of edge overlap over time.

    .. seealso:: The `Examples → Explore → Temporal edge matrix
        <../examples/basics.html#temporal-edge-matrix>`__  page for an example.

    .. rubric:: Example

    Loading and computing similarity among edge sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.example_sbm_graph()
        >>> tx.temporal_edge_matrix(TG, method="jaccard")

        [[1.0,  0.11, 0.11],
         [0.11, 1.0,  0.08],
         [0.11, 0.08, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: Measure to consider. Default is ``'jaccard'``. Available choices:

        - ``'jaccard'``: Jaccard similarity (intersection over union);

        - ``'intersect'``: intersection over size of first set;

        - ``'union'``: union over size of first set;

        - ``'geometric'``: geometric mean of set overlaps.

        - ``'dice'``: Dice coefficient (2 * intersection over sum of sizes).
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    data = {edge: i for i, edge in enumerate(TG.temporal_edges(copies=False))}
    data = [[data[edge] for edge in edges] for edges in TG.edges()]
    return _temporal_matrix(data, method=method, na_diag=na_diag)


def temporal_node_matrix(
    TG: TemporalGraph,
    method: Literal["jaccard", "union", "intersect", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns matrix of node overlap over time.

    .. rubric:: Example

    Loading and computing similarity among node sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.example_sbm_graph()
        >>> tx.temporal_node_matrix(TG, method="jaccard")

        [[1.0,  1.0,  0.99],
         [1.0,  1.0,  0.99],
         [0.99, 0.99, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: Measure to consider. Default is ``'jaccard'``. Available choices:

        - ``'jaccard'``: Jaccard similarity coefficient;

        - ``'intersect'``: intersection over size of first set;

        - ``'union'``: union over size of first set;

        - ``'geometric'``: geometric mean of set overlaps.

        - ``'dice'``: Dice coefficient (2 * intersection over sum of sizes).
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    return _temporal_matrix(TG.nodes(), method=method, na_diag=na_diag)


def _temporal_matrix(data: list, method: str, na_diag: bool = False) -> List[list]:
    values = []
    for i in range(len(data)):
        values.append([])
        for j in range(len(data)):
            if na_diag and i == j:
                values[i].append(None)
                continue
            data_i = set(data[i])
            data_j = set(data[j])
            intersection = data_i.intersection(data_j)
            union = data_i.union(data_j)
            if method == "jaccard":
                val = (len(intersection) / len(union)
                      ) if len(union) > 0 else 0
            elif method == "union":
                val = (len(union) / len(data_i)
                      ) if len(data_i) > 0 else 0
            elif method == "intersect":
                val = (len(intersection) / len(data_i)
                      ) if len(data_i) > 0 else 0
            elif method == "geometric":
                val = (len(intersection) ** 2 / (len(data_i) * len(data_j))
                      ) if len(data_i) > 0 and len(data_j) > 0 else 0
            elif method == "dice":
                val = (2 * len(intersection) / (len(data_i) + len(data_j))
                      ) if (len(data_i) + len(data_j)) > 0 else 0
            values[i].append(val)
    return values
