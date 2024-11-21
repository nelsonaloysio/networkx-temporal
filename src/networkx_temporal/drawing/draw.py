from typing import Optional, Union

import networkx as nx

from .networkx import draw_networkx
from ..typing import Figure, Literal, TemporalGraph

BACKEND = Literal["networkx"]


def draw(
    graph: Union[TemporalGraph, nx.Graph, list],
    backend: Optional[BACKEND] = "networkx",
    *args,
    **kwargs
) -> Figure:
    """
    Draw temporal graph using the specified renderer. By default,
    :func:`~networkx_temporal.drawing.draw_networkx` is used.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.graph.TemporalGraph`, a
        static graph, or a list of static graphs from NetworkX as input.
    :param str backend: Renderer to use. Optional. Default is ``'networkx'``.
    :param kwargs: Keyword arguments to pass to the renderer function.
    """
    assert backend is None or backend in BACKEND.__args__,\
        f"Unknown backend, must be one of: {BACKEND.__args__}."

    if not backend or backend == "networkx":
        return draw_networkx(graph, *args, **kwargs)
