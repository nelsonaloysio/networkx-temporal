import dynetx as dn
import networkx as nx


def nx2dn(G: nx.Graph, attr: str = "time", **kwargs):
    """
    Convert a NetworkX graph to a DyNetX graph.

    :param G: NetworkX graph object.
    :param attr: Attribute name for the temporal edges. Default is ``'time'``.
    """
    dnG = getattr(dn, f"Dyn{'Di' if G.is_directed() else ''}Graph")(**kwargs)

    for u, v, x in G.edges(data=True):
        dnG.add_interaction(u, v, t=x.get(attr, 0))

    return dnG
