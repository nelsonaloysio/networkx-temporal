from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx

DRAW_OPTS = {
    "arrows": True,
    "edge_color": "#00000050",
    "node_color": "#aaa",
    "node_size": 250,
    "with_labels": True
}


def draw_temporal_graph(
    TG,
    pos: Optional[dict] = None,
    layout: str = "kamada_kawai",
    nrows: int = 1,
    ncols: Optional[int] = None,
    figsize: tuple = (3, 3),
    suptitle: Optional[str] = None,
    temporal_opts: dict = {},
    **draw_opts
) -> plt.Figure:
    """
    Example code to draw a temporal graph(s).

    :param TG: Temporal graph or list of temporal graphs.
    :param pos: A dictionary with nodes as keys and positions as values.
    :param nrows: Number of rows in the figure.
    :param ncols: Number of columns in the figure.
    :param figsize: Tuple with the dimensions of the figure.
    :param suptitle: Title of the figure.
    :param temporal_opts: Dictionary with options for each temporal graph.
    :param draw_opts: Additional options for drawing the graph(s).
    """
    assert pos is None or type(pos) == dict,\
        "Argument `pos` must be a dictionary or None."

    assert nrows > 0,\
        "Argument `nrows` must be a positive integer."

    assert ncols is None or ncols > 0,\
        "Argument `ncols` must be a positive integer or None."

    assert figsize is None or type(figsize) == tuple,\
        "Argument `figsize` must be a tuple or None."

    assert suptitle is None or type(suptitle) == str,\
        "Argument `suptitle` must be a string or None."

    assert type(temporal_opts) == dict,\
        "Argument `temporal_opts` must be a dictionary."

    is_static = type(TG) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)

    if is_static:
        TG = [TG]  # Allows a single graph to be passed as input.

    fig, ax = plt.subplots(nrows=nrows,
                           ncols=ncols or len(TG) or 1,
                           figsize=figsize,
                           constrained_layout=True)

    i, j = 0, 0

    for t, G in enumerate(TG):
        ax_ = ax if is_static else ax[t] if nrows == 1 else ax[i, j]

        nx.draw(G,
                ax=ax_,
                pos=pos or getattr(nx, f"{layout}_layout")(G),
                **{**DRAW_OPTS, **draw_opts, **temporal_opts.get(t, {})})

        ax_.set_title("" if is_static else f"$t$ = {G.name or t}")

        j += 1
        if ncols and j % ncols == 0:
            j = 0
            i += 1

    if suptitle:
        plt.suptitle(suptitle)

    plt.close()

    return fig