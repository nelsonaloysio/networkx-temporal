from typing import Optional, Union

from .draw import draw, BACKEND
from ..typing import Figure, StaticGraph, TemporalGraph
from ..utils import is_temporal_graph

C0, C1 = "tab:red", "#333"


def draw_unrolled(
    UTG: Union[TemporalGraph, StaticGraph],
    backend: Optional[BACKEND] = "networkx",
    **kwargs
) -> Figure:
    """
    Draw unrolled temporal graph with set defaults.

    :param object UTG: A :class:`~networkx_temporal.classes.TemporalGraph` or unrolled
        graph object from :func:`~networkx_temporal.transform.to_unrolled`.
    :param str backend: Renderer to use. Optional. Default is ``'networkx'``.
    :param kwargs: Keyword arguments to pass to the renderer function.
    """
    assert backend is None or backend in BACKEND.__args__,\
        f"Unknown backend, must be one of: {BACKEND.__args__}."

    if is_temporal_graph(UTG):
        UTG = UTG.to_unrolled()

    if "pos" not in kwargs:
        kwargs["pos"] = unrolled_layout(UTG)

    if "figsize" not in kwargs:
        kwargs["figsize"] = (4.5, 4.5)

    if "node_size" not in kwargs:
        kwargs["node_size"] = 450

    if "labels" not in kwargs:
        kwargs["labels"] = {
            n: f"{n.split('_')[0]}$_{n.split('_')[1]}$" for n in UTG.nodes()}

    if "style" not in kwargs:
        kwargs["style"] = [
            "dotted" if u.split("_")[0] == v.split("_")[0] else "solid" for u, v in UTG.edges()]

    if not backend or backend == "networkx":
        return draw(UTG, **kwargs)


def unrolled_layout(
    UTG: Union[TemporalGraph, StaticGraph],
    nodes: Optional[list] = None,
) -> dict:
    """
    Compute unrolled temporal graph node positions.

    :param object UTG: A :class:`~networkx_temporal.classes.TemporalGraph` or unrolled
        graph object from :func:`~networkx_temporal.transform.to_unrolled`.
    :param nodes: A list of node identifiers to compute positions for.
        Useful for visualizing specific nodes or defining a particular ordering.
    """
    if is_temporal_graph(UTG):
        UTG = UTG.to_unrolled()

    if not nodes:
        nodes = sorted(
            set([n.rsplit("_")[0] for n in UTG.nodes()])
        )

    pos = {n: (int(n.rsplit("_")[1]), -nodes.index(n.rsplit("_")[0]))
            for n in UTG.nodes()}

    return pos
