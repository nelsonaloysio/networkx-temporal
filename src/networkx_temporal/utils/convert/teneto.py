from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_teneto(G: Union[StaticGraph, TemporalGraph, list], attr: str = "time"):
    """ Convert from NetworkX to `Teneto <https://teneto.readthedocs.readwrite>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param attr: Attribute name for the temporal edges. Default is ``'time'``.

    :rtype: teneto.TemporalNetwork
    """
    import teneto as tn

    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(G) or type(G) == list:
        return [to_teneto(H, attr=attr) for H in G]

    labels = {node: i for i, node in enumerate(G.nodes())}

    tnG = tn.TemporalNetwork()

    tnG.network_from_edgelist([
        (labels[u], labels[v], x.get(attr, 0), x.get("weight", 1))
        for u, v, x in G.edges(data=True)
    ])

    tnG.nodelabels = list(labels)
    return tnG
