from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_stellargraph(G: Union[StaticGraph, TemporalGraph, list], *args, **kwargs):
    """ Convert from NetworkX to `StellarGraph <https://stellargraph.readthedocs.readwrite/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: stellargraph.StellarGraph

    :note: Wrapper function for
        `stellargraph.StellarGraph.from_networkx
        <https://stellargraph.readthedocs.readwrite/en/latest/api.html#stellargraph.StellarGraph.from_networkx>`__.
    """
    import stellargraph as sg

    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(G) or type(G) == list:
        return [to_stellargraph(H, *args, **kwargs) for H in G]

    return sg.StellarGraph.from_networkx(G, *args, **kwargs)
