from collections import Counter
from typing import Optional, Union

import networkx as nx

from ..classes.factory import temporal_graph
from ..classes.functions import from_multigraph
from ..classes.types import is_static_graph
from ..typing import Literal, StaticGraph, TemporalGraph

DELTA = {"int": int, "float": float}


def from_events(
    events: list,
    directed: bool = None,
    multigraph: bool = None,
    as_view: bool = True,
    node_attrs: Optional[list] = None,
    edge_attrs: Optional[list] = None,
) -> TemporalGraph:
    """ Returns :class:`~networkx_temporal.classes.TemporalGraph` from edge-level events.
    Events are:

    - **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time
      attribute;

    - **4-tuples** (:math:`u, v, t, \\delta`), where :math:`\\delta` is either an
      integer for edge addition (``1``) or deletion (``-1``) event, or a float defining the
      duration of the pairwise interaction (zero for a single snapshot).

    .. seealso::

        The `Convert and transform → Graph representations
        <../examples/convert.html#graph-representations>`__
        page for details and examples.

    :param list events: List of 3-tuple or 4-tuple edge-level events.
    :param bool directed: If ``True``, returns as
        :class:`~networkx_temporal.classes.TemporalDiGraph` object.
    :param bool multigraph: If ``True`` (default), returns a `MultiGraph
        <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`_.
    :param as_view: If ``False``, returns copies instead of views of the original graph.
        Default is ``True``.
    :param node_attrs: List of node attributes to add to the temporal graph, one per event.
    :param edge_attrs: List of edge attributes to add to the temporal graph, one per event.
    """
    multigraph = True if multigraph is None else multigraph

    if len(events) == 0:
        raise ValueError("Events must be a non-empty list of 3 or 4-tuples.")
    if len(events[0]) not in (3, 4):
        raise ValueError(f"Each event must have 3 or 4 elements, received: {len(events[0])}.")
    if len(events[0]) == 4 and type(events[0][-1]) not in (int, float):
        raise ValueError("The fourth element of each event must be either an integer or a float.")

    G = getattr(nx, f"Multi{'Di' if directed else ''}Graph")()

    # (u, v, t)
    if len(events[0]) == 3:
        G.add_edges_from((u, v, {"time": t}) for u, v, t in events)

    # (u, v, t, e), where e is an integer in (-1, 1)
    elif len(events[0]) == 4 and type(events[0][-1]) == int:
        t_max = 1 + max(events, key=lambda x: x[2])[2]
        # Dictionary {(u, v) -> [range(t_start, t_end), ...]}
        temporal_edges = {}
        for u, v, t, e in events:
            if e == 1:
                temporal_edges[(u, v)] = temporal_edges.get((u, v), []) + [range(t, t_max)]
            elif e == -1:
                temporal_edges[(u, v)][-1] = range(temporal_edges[(u, v)][-1].start, t)
            else:
                raise ValueError(f"Expected edge events to be either 1 or -1, received: {e}.")
        # Add edges from temporal_edges dictionary as (u, v, t) tuples.
        G.add_edges_from(
            (u, v, {"time": t})
            for (u, v), ranges in temporal_edges.items() for r in ranges for t in r
        )

    # (u, v, t, e), where e is a (non-negative) float defining the duration of the interaction
    elif len(events[0]) == 4 and type(events[0][-1]) == float:
        for u, v, t, delta in events:
            G.add_edges_from(
                (u, v, {"time": i}) for i in range(t, t + 1 + int(delta))
            )

    TG = temporal_graph(directed=directed)
    TG.add_snapshot(G)
    TG = TG.slice(attr="time")

    if multigraph is False:
        # Check for duplicate edges before converting from multigraph to avoid data loss.
        TG = from_multigraph(TG)
        if G.size() != TG.size(copies=True):
            raise ValueError(
                "Events contain parallel edges, but `multigraph=False` was specified; please "
                "consider setting `multigraph=True` or removing duplicate events beforehand."
            )

    if not as_view:
        TG = TG.copy()

    if node_attrs is not None:
        attr_name = "node_attr" if type(next(iter(next(iter(node_attrs)).values()))) != dict else None
        for event, node_attr in zip(events, node_attrs):
            t = event[2]
            nx.set_node_attributes(TG[t], node_attr, attr_name)

    if edge_attrs is not None:
        edge_key = {}
        attr_name = "edge_attr" if type(next(iter(edge_attrs))) != dict else None
        for event, edge_attr in zip(events, edge_attrs):
            u, v, t = event[:3]
            if TG.is_multigraph():
                k = edge_key.get((u, v), -1) + 1
                edge = (u, v, k)
                edge_key[(u, v)] = k
            else:
                edge = (u, v)
            nx.set_edge_attributes(TG[t], {edge: edge_attr}, attr_name)

    return TG


def to_events(
    TG: Union[TemporalGraph, StaticGraph],
    delta: Optional[Literal["int", "float"]] = None,
    node_attrs: Optional[Union[str, list, bool]] = None,
    edge_attrs: Optional[Union[str, list, bool]] = None,
) -> list:
    """ Returns a list of edge-level events.

    - **3-tuples** (:math:`u, v, t`), where elements are the source node, target node, and time
      attribute;

    - **4-tuples** (:math:`u, v, t, \\delta`), where :math:`\\delta` is either an
      integer for edge addition (``1``) or deletion (``-1``) event, or a float defining the
      duration of the interaction (zero for a single snapshot).

    .. attention::

        As events are edge-based, node isolates without self-loops are not preserved.

    :param TemporalGraph TG: Temporal graph object.
    :param delta: Defines which additional parameter :math:`\\delta` should be returned.

        - If ``None``, returns events as 3-tuples. Default.

        - If ``'int'``, returns events as 4-tuples with an additional parameter representing
          edge addition (``1``) or deletion (``-1``) events.

        - If ``'float'``, returns events as 4-tuples with an additional parameter representing
          the duration of the pairwise interaction.

    :param node_attrs: Return node-event attributes as a separate list of elements.
        If ``None`` (default), no node attributes are returned. If a string or list of strings,
        returns the specified node attributes. If ``True``, returns all node attributes.
    :param edge_attrs: Return edge-event attributes as a separate list of elements.
        If ``None`` (default), no edge attributes are returned. If a string or list of strings,
        returns the specified edge attributes. If ``True``, returns all edge attributes.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    delta = DELTA.get(delta, delta)

    if is_static_graph(TG):
        TG = [TG]  # Allows a single graph to be passed as input.

    if delta not in (None, int, float):
        raise TypeError(f"Argument `delta` must be either `int` or `float` if provided.")
    # Filtered (frozen) multigraphs produce inconsistent results. [networkx/networkx#7724]
    if any(G.is_multigraph() and nx.is_frozen(G) for G in TG):
        raise ValueError(
            "Frozen multigraphs are not supported; consider calling the `copy` method beforehand."
        )

    # 3-tuples of format: (u, v, t).
    if not delta:
        events = [(e[0], e[1], t) for t, G in enumerate(TG) for e in G.edges()]

    # 4-tuples of format: (u, v, t, int_edge_addition_or_deletion).
    if delta == int:
        events = [(*edge, 0, 1) for edge in TG[0].edges()]
        for t in range(1, len(TG)):
            for edge in TG[t].edges():
                if not TG[t-1].has_edge(*edge):
                    events.append((*edge, t, 1))
            for edge in TG[t-1].edges():
                if not TG[t].has_edge(*edge):
                    events.append((*edge, t, -1))

    # 4-tuples of format: (u, v, t, float_edge_duration).
    if delta == float:
        events = []

        for i in range(len(TG)):
            for u, v in TG[i].edges():
                if i == 0 or not TG[i-1].has_edge(u, v):
                    for j in range(i+1, len(TG)):
                        if not TG[j].has_edge(u, v):
                            events.append((u, v, i, float(j - i - 1)))
                            break
                        if j == len(TG) - 1:
                            events.append((u, v, i, float(j - i)))
                            break
                    if i == len(TG) - 1:
                        events.append((u, v, i, 0.0))

    # Return node attribute(s) in a separate list if requested.
    if node_attrs is not None:
        node_attr_list = []
        if type(node_attrs) == str:
            k = node_attrs
        for e in events:
            u, v, t = e[:3]
            node_attr_list.append({
                n: TG[t].nodes[n].get(k, None)
                   if isinstance(node_attrs, str) else
                   {k: TG[t].nodes[n].get(k, None) for k in node_attrs}
                   if isinstance(node_attrs, list) else
                   TG[t].nodes[n]
                for n in e[:2]
            })
        if not edge_attrs:
            return events, node_attr_list

    # Return edge attribute(s) in a separate list if requested.
    if edge_attrs is not None:
        edge_key, edge_attr_list = 0, []
        if type(edge_attrs) == str:
            k = edge_attrs
        for i in range(len(events)):
            if edge_key > 0:
                # Skip already processed parallel edges in multigraphs while decrementing edge key.
                edge_key -= 1
                continue
            u, v, t = events[i][:3]
            data = TG[t].get_edge_data(u, v)
            if TG.is_multigraph():
                # Append all parallel edge attributes in the multigraph to list.
                for edge_key, data in data.items():
                    edge_attr_list.append(
                        data.get(k, None)
                        if isinstance(edge_attrs, str) else
                        {k: data.get(k, None) for k in edge_attrs}
                        if isinstance(edge_attrs, list) else
                        data
                    )
            else:
                edge_attr_list.append(
                    data.get(k, None)
                    if isinstance(edge_attrs, str) else
                    {k: data.get(k, None) for k in edge_attrs}
                    if isinstance(edge_attrs, list) else
                    data
                )
        if not node_attrs:
            return events, edge_attr_list

    return (events, node_attr_list, edge_attr_list) if node_attrs and edge_attrs else events
