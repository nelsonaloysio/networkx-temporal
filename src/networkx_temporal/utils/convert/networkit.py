from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_networkit(graph: Union[StaticGraph, TemporalGraph, list], *args, **kwargs):
    """ Convert from NetworkX to `Networkit <https://networkit.github.io/>`__.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: networkit.Graph

    :note: Wrapper function for
        `networkit.nxadapter.nx2nk
        <https://networkit.github.io/dev-docs/python_api/nxadapter.html#networkit.nxadapter.nx2nk>`__.
    """
    import networkit as nk

    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(graph) or type(graph) == list:
        return [to_networkit(g, *args, **kwargs) for g in graph]

    return nk.nxadapter.nx2nk(graph, *args, **kwargs)
