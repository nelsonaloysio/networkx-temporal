from typing import Any, List, Optional, Union

import networkx as nx
from networkx import NetworkXError

from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import StaticGraph, TemporalGraph, Literal


def combine_snapshots(graphs: List[TemporalGraph]) -> TemporalGraph:
    """ Returns the snapshot-wise union of multiple temporal graphs.

    Each snapshot in the resulting temporal graph is the union of the corresponding
    snapshots at each index :math:`t` from the input temporal graphs. All temporal graphs
    must have the same number of snapshots.

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

    TG.graphs.extend([
        nx.compose_all([temporal_graph[t] for temporal_graph in graphs])
        for t in range(len(graphs[0]))
    ])

    return TG


def edge_to_node_attr(
    TG: Union[StaticGraph, TemporalGraph],
    edge_attr: str,
    unique: bool = False,
) -> list:
    """ Returns node attributes aggregated from edge attributes.

    For temporal graphs, returns a list of dictionaries, one per snapshot, where
    each dictionary contains the aggregated edge attribute values for each node.

    :param object TG: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param edge_attr: The edge attribute key to aggregate.
    :param unique: Whether to discard duplicate attribute values.
        Default is ``False``.
    """
    if type(edge_attr) != str:
        raise TypeError(f"Argument `edge_attr` must be a string, received: {type(edge_attr)}.")
    if unique is not None and type(unique) != bool:
        raise TypeError(f"Argument `unique` must be a boolean, received: {type(unique)}.")

    if unique:
        node_attr = [{node: set() for node in G.nodes()}
                     for G in ([TG] if is_static_graph(TG) else TG)]

        for t, G in enumerate([TG] if is_static_graph(TG) else TG):
            for u, v, attr in G.edges(data=edge_attr):
                if attr is not None:
                    node_attr[t][u].add(attr)
                    node_attr[t][v].add(attr)

    else:
        node_attr = [{node: [] for node in G.nodes()}
                     for G in ([TG] if is_static_graph(TG) else TG)]

        for t, G in enumerate([TG] if is_static_graph(TG) else TG):
            for u, v, attr in G.edges(data=edge_attr):
                if attr is not None:
                    node_attr[t][u].append(attr)
                    node_attr[t][v].append(attr)

    return node_attr[0] if is_static_graph(TG) else node_attr


def get_edge_attributes(
    TG: TemporalGraph,
    attr: str,
) -> List[Any]:
    """ Returns the list of unique edge attribute values across all snapshots.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The edge attribute key.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")

    values = set()
    for G in TG:
        values.update(nx.get_edge_attributes(G, attr).values())
    return list(values)


def get_node_attributes(
    TG: TemporalGraph,
    attr: str,
) -> List[Any]:
    """ Returns the list of unique node attribute values across all snapshots.

    :param TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param attr: The node attribute key.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")

    values = dict()
    for t, G in enumerate(TG):
        values[t] = nx.get_node_attributes(G, attr)
    return list(values.values())


def node_to_edge_attr(
    TG: Union[StaticGraph, TemporalGraph],
    node_attr: str,
    origin: Literal["source", "target"] = "source",
) -> list:
    """ Returns edge attributes from node attributes.

    For temporal graphs, returns a list of lists, one per snapshot,
    where each list contains the source or target node attribute value for each edge.

    :param object TG: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param node_attr: The node attribute key to aggregate.
    :param origin: Whether to aggregate from ``source`` or ``target`` nodes.
    """
    if type(node_attr) != str:
        raise TypeError(f"Argument `node_attr` must be a string, received: {type(node_attr)}.")
    if origin not in ("source", "target"):
        raise ValueError(f"Argument `origin` must be one of ('source', 'target').")

    edge_attr = [[] for _ in ([TG] if is_static_graph(TG) else TG)]

    for t, G in enumerate([TG] if is_static_graph(TG) else TG):
        for u, v in G.edges():
            attr = G.nodes[u if origin == "source" else v].get(node_attr, None)
            if attr is not None:
                edge_attr[t].append(attr)

    return edge_attr[0] if is_static_graph(TG) else edge_attr


def partitions(
    TG: Optional[Union[TemporalGraph, StaticGraph]] = None,
    attr: Union[str, list, dict] = None,
    index: Optional[dict] = None,
) -> Union[list, dict]:
    """ Returns node partitions sharing the same attribute value.

    This function returns a list of dictionaries, one per snapshot in case of temporal graphs,
    where each dictionary contains the attribute values as keys and the corresponding nodes as
    values.

    The ``attr`` argument expects a node attribute key, a dictionary, or a list:

    - a ``str``, corresponding to the node attribute key to use for partitioning;
    - a ``dict``, where each key is a node and each value is the attribute value
      for that node;
    - a ``list``, where each value corresponds to an attribute value for each node;
    - a sequence of ``dict`` or ``list``, one per snapshot, if ``TG`` is a temporal graph.

    If ``index`` is ``True``, the node indices are returned instead of the node labels.
    Alternatively, if ``index`` is a dictionary, the node labels are mapped to the indices in the
    graph.

    .. rubric:: Examples

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalGraph()
       >>> TG.add_nodes_from(["a", "b", "c"], community=0)
       >>> TG.add_nodes_from(["d", "e", "f"], community=1)
       >>>
       >>> tx.partitions(TG, "community")

       [{0: ['a', 'b', 'c'], 1: ['d', 'e', 'f']}]

       >>> tx.partitions(TG, "community", index=True)

       [{0: [0, 1, 2], 1: [3, 4, 5]}]

    :param object TG: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param attr: Dictionary, list, or node attribute key for patitioning.
        Passing a sequence of lists or dictionaries is accepted for temporal graphs.
    :param index: Node index mapping. If ``True``, maps nodes to indices matching their ordering
        in the graph. Optional.
    """
    if not (TG is None or is_static_graph(TG) or is_temporal_graph(TG)):
        raise TypeError(
            f"Argument `TG` must be either a temporal or static graph, received: {type(TG)}."
        )
    if type(attr) not in (str, list, dict):
        raise TypeError(
            f"Argument `attr` must be one of (str, list, dict), received: {type(attr)}."
        )
    if index is not None and type(index) not in (dict, bool):
        raise TypeError(
            f"Argument `index` must be a boolean or dictionary, received: {type(index)}."
        )

    if is_static_graph(TG) and type(attr) == list:
        if len(attr) != TG.order():
            raise ValueError(
                f"Length of list `attr` ({len(attr)}) must match number of nodes ({TG.order()})."
            )
    elif is_temporal_graph(TG) and type(attr) == list:
        if len(attr) != len(TG):
            raise ValueError(
                f"Argument `attr` sequence length ({len(attr)}) must match number of snapshots ({len(TG)})."
            )
        if type(attr[0]) not in (list, dict):
            raise TypeError(
                f"Argument `attr` sequence must be one of (list, dict), received: {type(attr[0])}."
            )
        if not all(len(attr[i]) == TG[i].order() for i in range(len(attr))):
            raise ValueError(
                f"Argument `attr` sequences must each match the number of nodes in each snapshot."
            )

    if TG is None:
        if type(attr) != list:
            raise TypeError(
                "Argument `attr` must be a list or sequence of lists if graph is undefined."
            )
        if type(attr[0]) == list:
            partitions = []
            for snapshot_attr in attr:
                partition = [[] for _ in range(len(set(snapshot_attr)))]
                for i, value in enumerate(snapshot_attr):
                    partition[value].append(i)
                partitions.append(partition)
        else:
            partitions = [[] for _ in range(len(set(attr)))]
            for i, value in enumerate(attr):
                partitions[value].append(i)
        return partitions

    partitions = []

    for i, G in enumerate([TG] if is_static_graph(TG) else TG):
        attr_ = attr[i] if is_temporal_graph(TG) and type(attr) == list else attr

        if type(attr) == str:
            values = [value for node, value in G.nodes(data=attr)]
        if type(attr) == dict:
            values = [attr_[node] for node in G.nodes(data=attr)]
        if type(attr) == list:
            values = attr_

        partition = {v: [] for v in set(values)}
        mapping = dict(zip(range(G.order()), G.nodes()))

        if index:
            for i, key in enumerate(values):
                partition[key].append(index[mapping[i]])
        else:
            for i, key in enumerate(values):
                partition[key].append(mapping[i])

        partitions.append(partition)

    return partitions[0] if is_static_graph(TG) else partitions


def propagate_snapshots(
    TG: TemporalGraph,
    method: Literal["ffill", "bfill"] = "ffill",
    delta: Optional[int] = None,
) -> TemporalGraph:
    """ Propagates nodes and edges from earlier snapshots to later snapshots.

    Returns a temporal graph where each snapshot contains all nodes and edges
    from previous snapshots.

    :param object TG: :class:`~networkx_temporal.classes.TemporalGraph` object.
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
