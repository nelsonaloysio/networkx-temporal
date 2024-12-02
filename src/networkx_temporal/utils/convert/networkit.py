from typing import Union

from ..networkx import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_networkit(G: Union[TemporalGraph, StaticGraph, list], *args, **kwargs):
    """
    Convert from NetworkX to `Networkit <https://networkit.github.io/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.graph.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: networkit.Graph

    :note: Wrapper function for
        `networkit.nxadapter.nx2nk
        <https://networkit.github.io/dev-docs/python_api/nxadapter.html#networkit.nxadapter.nx2nk>`__.
    """
    import networkit as nk

    assert is_temporal_graph(G) or is_static_graph(G),\
        "Input must be a temporal or static NetworkX graph."

    if is_temporal_graph(G) or type(G) == list:
        return [to_networkit(H, *args, **kwargs) for H in G]

    return nk.nxadapter.nx2nk(G, *args, **kwargs)
