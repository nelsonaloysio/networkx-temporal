from typing import Optional, Union

from ..utils import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_dynetx(G: Union[TemporalGraph, StaticGraph, list], attr: Optional[str] = None, **kwargs):
    """
    Convert from NetworkX to `DyNetX <https://dynetx.readthedocs.readwrite/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param attr: Attribute name for the temporal edges. Optional.
    :param kwargs: Keyword arguments for the DyNetX graph object.

    :rtype: dynetx.DynGraph
    """
    import dynetx as dn

    assert attr is None or isinstance(attr, str),\
        "Attribute name must be a string."

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Input must be a temporal or static NetworkX graph."

    dnG = getattr(dn, f"Dyn{'Di' if G.is_directed() else ''}Graph")(**kwargs)

    if is_static_graph(G):
        G = [G]

    for i, H in enumerate(G):
        for u, v, t in H.edges(data=attr, default=i):
            dnG.add_interaction(u, v, t=t if attr is not None else i)

    return dnG
