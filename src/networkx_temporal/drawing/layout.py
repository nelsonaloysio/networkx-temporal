from typing import Callable, Union

import networkx as nx

from ..graph import is_temporal_graph
from ..typing import TemporalGraph


def layout(
    graph: Union[TemporalGraph, nx.Graph, list],
    *args,
    layout: Union[str, Callable] = "random",
    **kwargs
) -> dict:
    """
    Compute temporal node positions using the specified algorithm.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.graph.TemporalGraph`, a
        static graph, or a list of static graphs from NetworkX as input.
    :param layout: A callable or string with a `layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        from NetworkX to calculate node positions with. Default is ``'random'``.
    :param kwargs: Keyword arguments to pass to the layout function.
    """
    if not callable(layout):
        layout = getattr(nx, f"{(layout or 'random').replace('_layout', '')}_layout", None)

    assert layout is not None,\
        "Argument `layout` must be a string with a valid NetworkX layout algorithm."\
        f"Available choices: {[f for f in dir(nx) if f.endswith('_layout')]}"

    # Allow a single graph to be passed as input.
    if not is_temporal_graph(graph):
        return layout(graph, **kwargs)

    return [layout(G, *args, **kwargs) for G in graph]
