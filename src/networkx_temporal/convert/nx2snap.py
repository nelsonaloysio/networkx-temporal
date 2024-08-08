import snap


def nx2snap(G):
    """
    Convert a NetworkX graph to a Snap graph.
    """
    raise NotImplementedError("Method not implemented.")

    directed = G.is_directed()
    multigraph = G.is_multigraph()
    attributed = next(iter(G.nodes(data=True)))[-1] or next(iter(G.edges(data=True)))[-1]

    if directed:
        if multigraph:
            if attributed:
                H = snap.TNEANet.New()
            else:
                H = snap.TNEANet.New()
        else:
            if attributed:
                H = snap.TNEANet.New()
            else:
                H = snap.TNGraph.New()
