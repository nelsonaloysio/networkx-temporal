from typing import Optional, Union

import networkx as nx

from .convert import convert, FORMAT
from .snapshots import from_snapshots


def from_unified(UTG: nx.Graph) -> list:
    """
    Returns temporal graph from unified temporal graph (UTG).

    Note that the UTG must be a valid unified temporal graph, i.e., it must contain
    temporal nodes in the format `node_timestamp`, where `node` is the original node
    name and `timestamp` is a non-negative integer.

    :param UTG: Unified temporal graph.
    """
    temporal_nodes = {}

    for node in UTG.nodes():
        t = node.rsplit("_", 1)[-1]

        assert t.isdigit(),\
            f"Unified temporal graph (UTG) contains non-temporal nodes ('{node}')."

        temporal_nodes[t] = temporal_nodes.get(t, []) + [node]

    return from_snapshots([
        nx.relabel_nodes(
            UTG.subgraph(temporal_nodes[t]),
            {v: v.rsplit("_", 1)[0] for v in temporal_nodes[t]}
        )
        for t in sorted(temporal_nodes.keys(), key=int)
    ])


def to_unified(
    self,
    to: Optional[FORMAT] = None,
    add_couplings: bool = True,
    node_index: Optional[list] = None,
    relabel_nodes: Optional[Union[dict, list]] = None
) -> nx.Graph:
    """
    Returns a unified temporal graph (UTG).

    The UTG is a single graph that contains all the nodes and edges of an STG,
    plus proxy nodes and edge couplings connecting sequential temporal nodes.

    :param to: Format to convert the static graph to (optional).
    :param add_couplings: Add inter-slice edges among temporal nodes (default).
    :param node_index: Node index from static graph to include as attribute.
    :param relabel_nodes: Dictionary or list of dictionaries to relabel nodes.
        If a list, each dictionary is used to relabel nodes in a given snapshot.
        If a single dictionary, all nodes are relabeled using the same mapping.
        Not all nodes need to be included, but the list should have the same
        length as the number of snapshots. Any nodes not included in the mapping
        are by default relabeled as '{node}_{t}' for each time `t`. Examples:
        - List: [{"A": "A_0", "B": "B_0"}, {}, {"A": "A_0", "C": "C_2"}]
        - Dict: {"A": "A_0", "B": "B_0", "C": "C_2"}
    """
    T = range(len(self))
    order, size = self.temporal_order(), self.temporal_size()

    assert relabel_nodes is None or type(relabel_nodes) in (dict, list),\
        f"Argument 'relabel_nodes' must be a dict or list, received: {type(relabel_nodes)}."

    assert node_index is None or len(node_index) == len(set(node_index)),\
        "Repeated node indices are not allowed (are label types both strings and integers?)."

    # Create graph with intra-slice nodes and edges,
    # relabeling nodes to include temporal index.
    UTG = nx.compose_all([
        nx.relabel_nodes(
            self[t],
            {
                v:
                    relabel_nodes[t].get(v, f"{v}_{t}")
                    if type(relabel_nodes) == list else
                    relabel_nodes.get(v, f"{v}_{t}")
                    if type(relabel_nodes) == dict else
                    f"{v}_{t}"
                for v in self[t].nodes()
            }
        )
        for t in T
    ])

    # Add inter-slice couplings among temporal nodes.
    if add_couplings:
        for i in range(len(T)-1):
            for node in self[T[i]].nodes():
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

    # Avoid using last snapshot's name for the unified graph.
    UTG.name = f"{f'{self.name}' if self.name else 'UTG'} "\
                f"(t={len(self)}, proxy_nodes={len(UTG)-order}, edge_couplings={size-order})"

    if to:
        return convert(UTG, to)

    return UTG
