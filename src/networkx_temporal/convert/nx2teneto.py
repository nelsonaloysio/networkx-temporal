import teneto


def nx2teneto(G, attr: str = "time"):
    """
    Convert a NetworkX graph to a Teneto graph.
    """
    tn = teneto.TemporalNetwork()
    tn.network_from_edgelist(
        [(u, v, t) for u, v, t in G.edges(data=attr)]
    )
    return tn
