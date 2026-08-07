from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_teneto(graph: Union[StaticGraph, TemporalGraph, list], attr: str = "time"):
    """ Convert from NetworkX to `Teneto <https://teneto.readthedocs.io>`__.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param attr: Attribute name for the temporal edges. Default is ``'time'``.

    :rtype: teneto.TemporalNetwork
    """
    import teneto as tn

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(graph) or type(graph) == list:
        return [to_teneto(g, attr=attr) for g in graph]

    labels = {node: i for i, node in enumerate(graph.nodes())}

    tnG = tn.TemporalNetwork()

    tnG.network_from_edgelist([
        (labels[u], labels[v], x.get(attr, 0), x.get("weight", 1))
        for u, v, x in graph.edges(data=True)
    ])

    tnG.nodelabels = list(labels)
    return tnG
