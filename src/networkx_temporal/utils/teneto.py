import networkx as nx
import teneto


def nx2teneto(G: nx.Graph, attr: str = "time"):
    """
    Convert a NetworkX graph to a Teneto graph.

    :param G: NetworkX graph object.
    :param attr: Attribute name for the temporal edges. Default is ``'time'``.
    """
    labels = {node: i for i, node in enumerate(G.nodes())}

    tnG = teneto.TemporalNetwork()

    tnG.network_from_edgelist([
        (labels[u], labels[v], x.get(attr, 0), x.get("weight", 1))
        for u, v, x in G.edges(data=True)
    ])

    tnG.nodelabels = list(labels)
    return tnG
