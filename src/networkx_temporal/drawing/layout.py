from typing import Callable, Optional, Union

import networkx as nx

from ..classes.types import is_static_graph, is_unrolled_graph
from ..typing import StaticGraph, TemporalGraph


def layout(
    TG: Union[TemporalGraph, StaticGraph],
    layout: Union[str, Callable] = "random",
    *args,
    **kwargs
) -> dict:
    """ Compute temporal node positions with algorithm.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param layout: A callable or string, e.g., with a `layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        from NetworkX to calculate node positions with. Default is ``'random'``.
    :param kwargs: Keyword arguments to pass to the layout function.
    """
    layout_func = _layout_func(layout)

    if is_static_graph(TG):
        return layout_func(TG, **kwargs)

    return [layout_func(G, *args, **kwargs) for G in TG]


def unrolled_layout(
    UTG: StaticGraph,
    nodes: Optional[list] = None,
) -> dict:
    """ Compute unrolled temporal graph node positions.

    :param object UTG: A :class:`~networkx_temporal.classes.TemporalGraph` or unrolled
    :param nodes: A list of node identifiers to sort the layout by.
    """
    if not is_unrolled_graph(UTG):
        raise TypeError("Argument `UTG` must be a static unrolled temporal graph.")

    if not nodes:
        nodes = sorted(
            set([n.rsplit("_")[0] for n in UTG.nodes()])
        )
    pos = {node: (int(node.rsplit("_")[1]), -nodes.index(node.rsplit("_")[0]))
            for node in UTG.nodes()}

    return pos


def _layout_func(layout):
    """ Returns a layout function from a string or callable. """
    if callable(layout):
        return layout
    if type(layout) == str:
        layout = f"{(layout or 'random').replace('_layout', '')}_layout"

    if layout == "unrolled_layout":
        return unrolled_layout
    if layout in dir(nx):
        return getattr(nx, layout)

    layouts = ["unrolled_layout"]
    nx_layouts = [f for f in dir(nx) if f.endswith("_layout")]

    raise ValueError(
        f"Argument `layout` must be a callable or one of: {sorted(layouts + nx_layouts)}."
    )