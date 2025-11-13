from typing import Callable, Optional, Union

import networkx as nx

from ..classes.types import is_static_graph, is_unrolled_graph
from ..typing import StaticGraph, TemporalGraph


def layout(
    TG: Union[StaticGraph, TemporalGraph],
    layout: Union[str, Callable] = "random",
    *args,
    **kwargs
) -> dict:
    """ Compute temporal node positions with algorithm.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param layout: A callable or string, e.g., with a `layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        from NetworkX to calculate node positions with. Default is ``'random'``.
    :param kwargs: Keyword arguments to pass to the layout function.
    """
    layouts = [f for f in dir(nx) if f.endswith("_layout")]
    layouts += ["unrolled_layout"]

    if not callable(layout):
        layout = f"{(layout or 'random').replace('_layout', '')}_layout"
    if type(layout) == str and layout not in layouts:
        raise ValueError(
            "Argument `layout` must be a callable or a valid layout string."
            f"Choices: {sorted(layouts)}."
        )

    if layout == "unrolled_layout":
        layout = unrolled_layout
    else:
        layout = getattr(nx, layout)

    if is_static_graph(TG):
        return layout(TG, **kwargs)

    return [layout(G, *args, **kwargs) for G in TG]


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
