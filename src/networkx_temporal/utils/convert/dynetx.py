from typing import Optional, Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_dynetx(graph: Union[StaticGraph, TemporalGraph, list], attr: Optional[str] = None, **kwargs):
    """ Convert from NetworkX to `DyNetX <https://dynetx.readthedocs.io/>`__.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param attr: Attribute name for the temporal edges. Optional.
    :param kwargs: Keyword arguments for the DyNetX graph object.

    :rtype: dynetx.DynGraph
    """
    import dynetx as dn

    if attr is not None and type(attr) != str:
        raise TypeError("Attribute name must be a string.")

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    dnG = getattr(dn, f"Dyn{'Di' if graph.is_directed() else ''}Graph")(**kwargs)

    if is_static_graph(graph):
        graph = [graph]

    for i, g in enumerate(graph):
        for u, v, t in g.edges(data=attr, default=i):
            dnG.add_interaction(u, v, t=t if attr is not None else i)

    return dnG
