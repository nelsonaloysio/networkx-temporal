from typing import Any


def neighbors(self, node: Any):
    """
    Returns neighbors of a node considering each snapshot.

    :param node: Node in the temporal graph.

    :meta private:
    """
    return list(list(G.neighbors(node)) if G.has_node(node) else [] for G in self)
