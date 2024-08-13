import networkx as nx
import teneto


def nx2teneto(G: nx.Graph, attr: str = "time"):
    """
    Convert a NetworkX graph to a Teneto graph.

    :param G: NetworkX graph object.
    :param attr: Attribute name for the temporal edges. Default is `"time"`.
    """
    tnG = teneto.TemporalNetwork()
    tnG.network_from_edgelist(
        [(u, v, t) for u, v, t in G.edges(data=attr)]
    )
    return tnG
