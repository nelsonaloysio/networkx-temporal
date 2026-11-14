from typing import Union

from ...classes.types import is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_stellargraph(graph: Union[StaticGraph, TemporalGraph], *args, **kwargs):
    """ Convert from NetworkX to `StellarGraph <https://stellargraph.readthedocs.io/>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: stellargraph.StellarGraph

    :note: Wrapper function for
        `stellargraph.StellarGraph.from_networkx
        <https://stellargraph.readthedocs.io/en/latest/api.html#stellargraph.StellarGraph.from_networkx>`__.
    """
    import stellargraph as sg

    if is_temporal_graph(graph):
        return [to_stellargraph(g, *args, **kwargs) for g in graph]

    return sg.StellarGraph.from_networkx(graph, *args, **kwargs)
