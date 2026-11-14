from typing import Union

from ...classes.types import is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_networkit(graph: Union[StaticGraph, TemporalGraph], *args, **kwargs):
    """ Convert from NetworkX to `Networkit <https://networkit.github.io/>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: networkit.Graph

    :note: Wrapper function for
        `networkit.nxadapter.nx2nk
        <https://networkit.github.io/dev-docs/python_api/nxadapter.html#networkit.nxadapter.nx2nk>`__.
    """
    import networkit as nk

    if is_temporal_graph(graph):
        return [to_networkit(g, *args, **kwargs) for g in graph]

    return nk.nxadapter.nx2nk(graph, *args, **kwargs)
