from typing import Optional, Union

import networkx as nx

from .snapshots import from_snapshots
from ..typing import StaticGraph, TemporalGraph
from ..utils.convert import convert, FORMATS


def from_unrolled(UTG: StaticGraph) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.classes.TemporalGraph` from an unrolled graph.

    Unrolled graphs are a static representation of temporal networks, where each node is suffixed
    with its temporal index (e.g., ``'a_0'``) and inter-slice edges are added to connect copies of
    the same node at different time steps (e.g., ``'a_0'`` and ``'a_1'``), resulting in increased
    order and size.

    .. attention::

        Dynamic graph-level attributes are not preserved in this representation of temporal graphs.

    :param UTG: Unrolled temporal graph.
    """
    temporal_nodes = {}

    for node in UTG.nodes():
        t = node.rsplit("_", 1)[-1]

        assert t.isdigit(),\
            f"Unrolled temporal graph (UTG) contains non-temporal nodes ('{node}')."

        temporal_nodes[t] = temporal_nodes.get(t, []) + [node]

    return from_snapshots([
        nx.relabel_nodes(
            UTG.subgraph(temporal_nodes[t]),
            {v: v.rsplit("_", 1)[0] for v in temporal_nodes[t]}
        )
        for t in sorted(temporal_nodes.keys(), key=int)
    ])


def to_unrolled(
    TG: TemporalGraph,
    to: Optional[FORMATS] = None,
    add_couplings: bool = True,
    node_index: Optional[list] = None,
    relabel_nodes: Optional[Union[dict, list]] = None
) -> StaticGraph:
    """
    Returns an unrolled temporal graph.

    An unrolled temporal graph is a single graph containing all the nodes and edges of its
    snapshots, plus additional time-adjacent node copies and edge couplings connecting them.

    .. seealso::

        The `Examples → Convert and transform → Unrolled temporal graph
        <../examples/convert.html#tg-utg>`__
        page for an example.

    :param TemporalGraph TG: Temporal graph object.
    :param str to: Package name or alias to :func:`~networkx_temporal.utils.convert.convert`
        the graph. Optional.
    :param add_couplings: Add inter-slice edges among temporal nodes. Default is ``True``.
    :param node_index: Node index from static graph to include as node-level attribute. Optional.
    :param relabel_nodes: Dictionary or list of dictionaries to relabel nodes.
        If a list, each dictionary is used to relabel nodes in a given snapshot.
        If a single dictionary, all nodes are relabeled using the same mapping.
        Not all nodes need to be included, but the list should have the same
        length as the number of snapshots. Any nodes not included in the mapping
        are by default relabeled as ``'{name}_{t}'`` for each time ``t``. Examples:

        - **list**: ``[{"a": "a_0", "b": "b_0"}, {}, {"a": "a_0", "c": "c_2"}]``

        - **dictionary**: ``{"a": "a_0", "b": "b_0", "c": "c_2"}``

    :note: Available both as a function and as a method from :class:`~networkx_temporal.classes.TemporalGraph` objects.
    """
    T = range(len(TG))
    order = TG.temporal_order()

    assert relabel_nodes is None or type(relabel_nodes) in (dict, list),\
        f"Argument 'relabel_nodes' must be a dict or list, received: {type(relabel_nodes)}."

    assert node_index is None or len(node_index) == len(set(node_index)),\
        "Repeated node indices are not allowed (are label types both strings and integers?)."

    # Create graph with intra-slice nodes and edges,
    # relabeling nodes to include temporal index.
    UTG = nx.compose_all([
        nx.relabel_nodes(
            TG[t],
            {
                v:
                    relabel_nodes[t].get(v, f"{v}_{t}")
                    if type(relabel_nodes) == list else
                    relabel_nodes.get(v, f"{v}_{t}")
                    if type(relabel_nodes) == dict else
                    f"{v}_{t}"
                for v in TG[t].nodes()
            }
        )
        for t in T
    ])

    # Add inter-slice couplings among temporal nodes.
    if add_couplings:
        for i in range(len(T)-1):
            for node in TG[T[i]].nodes():
                if UTG.has_node(f"{node}_{T[i]}"):
                    for j in range(i+1, len(T)):
                        if UTG.has_node(f"{node}_{T[j]}"):
                            UTG.add_edge(f"{node}_{T[i]}", f"{node}_{T[j]}")
                            break

    # Add temporal node indices as attributes.
    if node_index:
        node_index = [str(v) for v in node_index]
        nx.set_node_attributes(
            UTG,
            {node: node_index.index(node.rsplit("_", 1)[0]) for node in UTG.nodes()},
            "node_index"
        )

    # Avoid using last snapshot's name for the unrolled graph.
    UTG.name = f"{f'{TG.name}' if TG.name else 'UTG'} ("\
               f"t={len(TG)}, "\
               f"node_copies={UTG.order()-order}, "\
               f"edge_couplings={True if add_couplings else False})"

    # Convert graph object to desired format.
    if to:
        return convert(UTG, to)

    return UTG
