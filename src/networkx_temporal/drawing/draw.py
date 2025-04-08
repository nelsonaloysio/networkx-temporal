from typing import Optional, Union

from .networkx import draw_networkx
from ..typing import Figure, Literal, StaticGraph, TemporalGraph

BACKEND = Literal["networkx"]


def draw(
    TG: Union[TemporalGraph, StaticGraph],
    backend: Optional[BACKEND] = "networkx",
    *args,
    **kwargs
) -> Figure:
    """
    Plot temporal graph using the specified renderer. By default,
    :func:`~networkx_temporal.drawing.draw_networkx` is used.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param str backend: Renderer to use. Optional. Default is ``'networkx'``.
    :param kwargs: Keyword arguments to pass to the renderer function.
    """
    assert backend is None or backend in BACKEND.__args__,\
        f"Unknown backend, must be one of: {BACKEND.__args__}."

    if not backend or backend == "networkx":
        return draw_networkx(TG, *args, **kwargs)
