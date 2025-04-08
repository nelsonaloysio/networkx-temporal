from typing import Any, Optional, Union

import networkx as nx

from ..typing import StaticGraph, TemporalGraph


def from_multigraph(G: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """
    Returns a graph from a multigraph object.

    Parallel (multiple) edges among nodes are converted to single edges, with a ``weight`` attribute
    storing their total occurrences. If the attribute already exists, their total sum is stored instead.

    .. attention::

        Converting a multigraph to a graph object may result in data loss: multiple parwise edges
        are merged into single ones, with later edge attributes taking precedence over earlier ones.

    .. rubric:: Example

    .. code-block:: python

       >>> import networkx as nx
       >>> from networkx_temporal import from_multigraph
       >>>
       >>> G = nx.MultiGraph()
       >>> G.add_edge(1, 2, weight=2)
       >>> G.add_edge(1, 2, weight=3)
       >>>
       >>> H = from_multigraph(G)
       >>> print(H.edges(data=True))

       [(1, 2, {'weight': 5})]

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from ..classes import temporal_graph

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Argument `graph` must be either a temporal or static NetworkX graph object."

    if not is_temporal_graph(G):
        return _from_multigraph(G)

    TG = temporal_graph(directed=G.is_directed(), multigraph=False)
    TG.data = [_from_multigraph(H) for H in G]
    TG.name = G.name
    TG.names = G.names
    return TG


def is_frozen(TG: Union[TemporalGraph, StaticGraph]) -> bool:
    """
    Returns ``True`` if graph is frozen, ``False`` otherwise.

    A frozen graph is immutable, meaning that nodes and edges cannot be added or removed.
    Calling ``copy`` on a frozen graph returns a (mutable) deep copy of the graph object.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    """
    assert is_temporal_graph(TG) or is_static_graph(TG),\
        "Argument `graph` must be a temporal graph or a static graph."

    if is_static_graph(TG):
        return nx.is_frozen(TG)

    return [nx.is_frozen(G) for G in TG]


def is_static_graph(obj: Any) -> bool:
    """
    Returns ``True`` if object is a static graph, ``False`` otherwise.

    Matches any of: NetworkX
    `Graph <https://networkx.org/documentation/stable/reference/classes/graph.html>`__,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__,
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__.

    :param obj: Object to check.
    """
    return not is_temporal_graph(obj) and isinstance(obj, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph))


def is_temporal_graph(obj: Any) -> bool:
    """
    Returns ``True`` if object is a temporal graph, ``False`` otherwise.

    Matches any of:
    :class:`~networkx_temporal.classes.TemporalGraph`,
    :class:`~networkx_temporal.classes.TemporalDiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiGraph`,
    :class:`~networkx_temporal.classes.TemporalMultiDiGraph`.

    :param obj: Object to check.
    """
    from ..classes import TemporalABC, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    return isinstance(obj, (TemporalABC, TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph))


def partitions(
    G: Union[TemporalGraph, StaticGraph],
    attr: Union[str, list, dict],
    index: Optional[dict] = None,
) -> Union[list, dict]:
    """
    Returns node partitions sharing the same attribute value.

    The ``attr`` argument can be a node attribute key, a dictionary, or a list:

    - a ``str``, corresponding to the node attribute key to use for partitioning;
    - a ``dict``, where each key is a node and each value is the attribute value
        for that node,
    - a ``list``, where each value corresponds to an attribute value for each node,
    - a sequence of ``dict`` or ``list``, one per snapshot, if the graph is temporal.

    If ``index`` is ``True``, the node indices are returned instead of the node labels.
    If ``index`` is a dictionary, the node labels are mapped to the indices in the graph.

    The function returns a list of dictionaries, one per snapshot, where each dictionary
    contains the attribute values as keys and the corresponding nodes as values, or a single
    dictionary if the graph is static.

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
    assert type(attr) in (str, list, dict), \
        f"Argument `attr` must be one of (str, list, dict), received: {type(attr)}."
    assert index is None or type(index) in (dict, bool),\
        f"Argument `index` must be a boolean or dictionary, received: {type(index)}."

    if is_static_graph(G) and type(attr) == list:
        assert len(attr) == G.order(),\
            f"Length of list `attr` ({len(attr)}) must match number of nodes ({G.order()})."

    elif is_temporal_graph(G) and type(attr) == list:
        assert len(attr) == len(G),\
            f"Argument `attr` sequence length ({len(attr)}) must match number of snapshots ({len(G)})."
        assert type(attr[0]) in (list, dict),\
            f"Argument `attr` sequence must be one of (list, dict), received: {type(attr[0])}."
        assert all(len(attr[i]) == G[i].order() for i in range(len(attr))),\
            f"Argument `attr` sequence of lists must each match the number of nodes in each snapshot."

    partitions = []

    for i, G in enumerate([G] if is_static_graph(G) else G):
        attr_ = attr[i] if is_temporal_graph(G) and type(attr) == list else attr

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

    return partitions[0] if is_static_graph(G) else partitions


def to_multigraph(G: Union[TemporalGraph, StaticGraph]) -> Union[TemporalGraph, StaticGraph]:
    """
    Returns a multigraph from a graph object.

    A multigraph is a graph that allows multiple (parallel) edges between pairwise nodes.

    .. seealso::

        The :func:`~networkx_temporal.utils.from_multigraph`
        function to convert a multigraph to a graph object.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    """
    from ..classes import temporal_graph

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Argument `graph` must be either a temporal or NetworkX graph object."

    if not is_temporal_graph(G):
        return _to_multigraph(G)

    TG = temporal_graph(directed=G.is_directed(), multigraph=True)
    TG.data = [_to_multigraph(H) for H in G]
    TG.name = G.name
    TG.names = G.names
    return TG


def _from_multigraph(G: nx.MultiGraph) -> StaticGraph:
    """ Returns a multigraph object from a graph. """
    H = getattr(nx, f"{f'Di' if G.is_directed() else ''}Graph")()
    H.add_edges_from(G.edges(data=True))

    weight = {}
    for u, v, w in G.edges(data="weight", default=1):
        weight[(u, v)] = weight.get((u, v), 0) + w

    nx.set_edge_attributes(H, weight, "weight")
    return H


def _to_multigraph(G: nx.MultiGraph) -> StaticGraph:
    """ Returns a graph object from a multigraph. """
    H = getattr(nx, f"Multi{f'Di' if G.is_directed() else ''}Graph")()
    H.add_nodes_from(G.nodes(data=True))
    H.add_edges_from(G.edges(data=True))
    return H
