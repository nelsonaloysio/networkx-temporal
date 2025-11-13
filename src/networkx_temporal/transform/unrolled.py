from typing import Optional, Union

import networkx as nx

from .snapshots import from_snapshots
from ..typing import Literal, StaticGraph, TemporalGraph
from ..utils.convert import convert, FORMATS


def from_unrolled(UTG: StaticGraph, delta: Optional[int] = None) -> TemporalGraph:
    """ Returns :class:`~networkx_temporal.classes.TemporalGraph` from an unrolled graph.

    Unrolled graphs are a static representation of temporal networks, where each node is suffixed
    with its temporal index (e.g., ``'a_0'``) and inter-slice edges are added to connect copies of
    the same node at different time steps (e.g., ``'a_0'`` and ``'a_1'``), resulting in increased
    order and size.

    If ``delta`` is set, edges are mapped to their original time steps based on the time step
    difference between source and target temporal nodes, :math:`(u_{t}, v_{t-\\delta})`. If unset,
    the ``delta`` attribute from the unrolled temporal graph is used, or ``0`` by default.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.from_events([
        >>>     ('a', 'b', 0),
        >>>     ('c', 'b', 1),
        >>>     ('a', 'c', 2),
        >>>     ('d', 'c', 2),
        >>>     ('d', 'e', 2),
        >>>     ('f', 'e', 3),
        >>>     ('f', 'a', 3),
        >>>     ('f', 'b', 3)
        >>> ])
        >>>
        >>> UTG = TG.to_unrolled()
        >>>
        >>> node_color = [
        >>>     "tab:red" if int(n.split("_")[1]) == TG.index_node(n.split("_")[0])[0] else "#333"
        >>>     for n in UTG.nodes()]
        >>>
        >>> tx.draw(UTG,
        >>>         layout=tx.unrolled_layout,
        >>>         labels={n: f"{n.split('_')[0]}$_{n.split('_')[1]}$" for n in UTG.nodes()},
        >>>         node_color=node_color,
        >>>         font_size=10,
        >>>         title="Unrolled Temporal Graph",
        >>>         connectionstyle="arc3,rad=0.25")

    .. image:: ../../assets/figure/transform/from_unrolled.png
        :align: center

    .. attention::

        As a static graph, unrolled graphs do not preserve graph-level temporal attributes.

    :param UTG: Unrolled temporal graph.
    :param delta: Time step between temporal nodes. Optional.
    """
    delta = getattr(UTG, "delta", 0)

    temporal_nodes = {}
    temporal_edges = {}

    edge_kwargs = {"data": True, **({"keys": True} if UTG.is_multigraph() else {})}

    for edge in UTG.edges(**edge_kwargs):
        u, u_t = edge[0].rsplit("_", 1)  # Original label and time step of source node.
        v, v_t = edge[1].rsplit("_", 1)  # Original label and time step of target node.

        if not u_t.isdigit():
            raise ValueError(f"Unrolled temporal graph (UTG) contains non-temporal nodes ('{u}').")
        if not v_t.isdigit():
            raise ValueError(f"Unrolled temporal graph (UTG) contains non-temporal nodes ('{v}').")

        # Determine time step of the edge based on `delta`.
        t = int(v_t) + (edge[-1][delta] if type(delta) == str else delta)

        # Skip inter-slice edges among temporal node copies.
        if edge[-1].get("coupling", False):
            continue

        # Map edges to original time steps.
        temporal_edges[t] = temporal_edges.get(t, []) + [edge[:-1]]

        # Map temporal nodes to original node labels.
        temporal_nodes[t] = temporal_nodes.get(t, set()) | set([edge[0], edge[1]])

    return from_snapshots([
        nx.relabel_nodes(
            UTG.edge_subgraph(temporal_edges[t]),
            {n: n.rsplit("_", 1)[0] for n in temporal_nodes[t]}
        )
        for t in sorted(temporal_edges.keys(), key=int)
    ])


def to_unrolled(
    TG: TemporalGraph,
    to: Optional[FORMATS] = None,
    delta: Optional[Union[int, str]] = 0,
    edge_couplings: bool = True,
    node_copies: Optional[Literal["all", "fill", "persist"]] = None,
    node_index: Optional[list] = None,
) -> StaticGraph:
    """ Returns an unrolled temporal graph.

    An unrolled temporal graph is a single graph containing all nodes and edges in all
    snapshots, plus time-adjacent node copies and edge couplings which connect these copies.

    If ``delta`` is set, edges are added between temporal nodes in sequential time steps,
    :math:`(u_{t}, v_{t+\\delta})`, resulting in time series representations [0]_ of temporal
    networks.

    .. seealso::

        The `Examples → Convert and transform → Unrolled temporal graph
        <../examples/convert.html#tg-utg>`__
        page for examples.

    .. [0] Hyoungshick, K., Anderson, R. (2012). ''Temporal node centrality in complex networks''.
        Physical Review E, 85(2). doi: `10.1103/PhysRevE.85.026107
        <https://doi.org/10.1103/PhysRevE.85.026107>`__

    :param TemporalGraph TG: Temporal graph object.
    :param str to: Package name or alias to :func:`~networkx_temporal.utils.convert.convert`
        the graph. Optional.
    :param delta: Time step between temporal nodes. Accepts an integer or a string
        with the edge-level attribute key name. Default: ``0``.
    :param edge_couplings: Add inter-slice edges among temporal nodes. Default: ``True``.
    :param node_copies: Control inter-slice couplings among temporal node copies. Optional.

        - ``'all'``: add temporal node copies to all snapshots.

        - ``'persist'``: add temporal node copies to all future snapshots.

        - ``'fill'``: add temporal node copies in between snapshots.

    :param node_index: Store node index from static graph as node-level attribute ``'node_index'``.
        Optional.

    :note: Available both as a function and as a method from
        :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    T = range(len(TG))
    node_copies = node_copies.lower() if type(node_copies) == str else node_copies

    if delta is not None and (type(delta) != int or delta < 0):
        raise TypeError(
            "Argument `delta` must be a non-negative integer."
        )
    if node_copies not in (None, "all", "fill", "persist"):
        raise ValueError(
            "Argument `node_copies` not in ('all', 'fill', 'persist')."
        )
    if node_index is not None and len(node_index) != len(set(node_index)):
        raise ValueError(
            "Duplicated `node_index` values (are label types both strings and integers?)."
        )

    UTG = TG.new_snapshot()

    if type(delta) == str:
        UTG.add_edges_from([
            (f"{u}_{t}", f"{v}_{t+d or 0}")
            for t in T
            for u, v, d in TG[t].edges(data=delta)
        ])
    else:
        UTG.add_edges_from([
            (f"{u}_{t}", f"{v}_{t+delta or 0}")
            for t in T
            for u, v in TG[t].edges()
        ])

    # Add inter-slice couplings among temporal nodes in all snapshots.
    if node_copies == "all":
        UTG.add_nodes_from([
            f"{n}_{t}"
            for t in range(len(T)+delta)
            for n in TG.temporal_nodes()
        ])

    # Add more couplings among node copies.
    if node_copies in ("fill", "persist"):
        UTG_nodes = list(UTG.nodes())
        for node in UTG_nodes:
            node, t = node.rsplit("_", 1)
            if node_copies == "persist" or any(UTG.has_node(f"{node}_{j}") for j in range(int(t)+1, len(T)+delta)):
                UTG.add_nodes_from([(f"{node}_{j}") for j in range(int(t)+1, len(T)+delta)])

    # Add inter-slice couplings among temporal nodes.
    if edge_couplings:
        UTG_nodes = list(UTG.nodes())
        for node in UTG_nodes:
            node, t = node.rsplit("_", 1)
            for j in range(int(t)+1, len(T)+delta):
                if UTG.has_node(f"{node}_{j}"):
                    UTG.add_edge(f"{node}_{t}", f"{node}_{j}", coupling=True)
                    break

    # Add temporal node indices as attributes.
    if node_index:
        node_index = [str(v) for v in node_index]
        nx.set_node_attributes(
            UTG,
            {node: node_index.index(node.rsplit("_", 1)[0]) for node in UTG.nodes()},
            "node_index"
        )

    # Set name and `delta` attribute.
    UTG.name = 'UnrolledTemporalGraph'
    UTG.delta = delta

    # Convert graph object to desired format.
    if to:
        return convert(UTG, to)

    return UTG
