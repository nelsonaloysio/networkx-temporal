from typing import Optional, Union

import networkx as nx

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from ..typing import TemporalGraph, Figure

DRAW_OPTS = {
    "arrows": True,
    "edge_color": "#00000050",
    "node_color": "#aaa",
    "node_size": 250,
    "with_labels": True
}


def draw(
    TG: Union[TemporalGraph, nx.Graph, list],
    figsize: tuple = (3, 3),
    pos: Optional[dict] = None,
    layout: Optional[str] = "random",
    nrows: Optional[int] = 1,
    ncols: Optional[int] = None,
    names: Optional[bool] = None,
    suptitle: Optional[str] = None,
    temporal_opts: Union[list, dict] = None,
    layout_opts: Union[list, dict] = None,
    **draw_opts
) -> Figure:
    """
    Wrapper method around `NetworkX's draw
    <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
    function. Requires `matplotlib <https://pypi.org/project/matplotlib/>`__.

    Returns a `matplotlib Figure <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__
    with temporal graph snapshots as subplots.
    Node positions can be provided as a dictionary or computed using one of `NetworkX's layout algorithms
    <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__.
    The figure may be further customized by setting ``draw_opts``, ``temporal_opts``, and ``layout_opts``.

    .. rubric:: Example

    .. code-block:: python

        >>> # !pip install matplotlib
        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.TemporalGraph(directed=True, multigraph=True)
        >>>
        >>> TG.add_edges_from([
        >>>     ("a", "b", {"time": 0}),
        >>>     ("c", "b", {"time": 1}),
        >>>     ("d", "c", {"time": 2}),
        >>>     ("d", "e", {"time": 2}),
        >>>     ("a", "c", {"time": 2}),
        >>>     ("f", "e", {"time": 3}),
        >>>     ("f", "a", {"time": 3}),
        >>>     ("f", "b", {"time": 3}),
        >>> ])
        >>>
        >>> TG = TG.slice(attr="time")
        >>>
        >>> fig = tx.draw(TG, layout="kamada_kawai", figsize=(8, 2))
        >>> # fig.savefig("figure.png")
        >>>
        >>> fig.show()

    .. image:: ../../figure/fig-0.png

    .. important::

        This function simply calls `NetworkX's draw
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
        in the backend and returns a `matplotlib Figure
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__ with
        temporal graph snapshots as subplots. It does not scale well to large graphs, which usually
        require more sophisticated approaches or specialized visualization tools.

    .. seealso::

        The `Examples: Slice temporal graph
        <https://networkx-temporal.readthedocs.io/en/latest/examples/basics.html#slice-temporal-graph>`__
        and `Examples: Community detection
        <https://networkx-temporal.readthedocs.io/en/latest/examples/community.html>`__
        pages for more.

    :param TG: :class:`~networkx_temporal.TemporalGraph` or NetworkX graph object(s).
    :param figsize: Tuple with the dimensions of the figure. Default is ``(3, 3)``.
    :param pos: A dictionary with nodes as keys and positions as values. Optional.
    :param layout: Layout algorithm to use when ``pos`` is not provided. Optional.
        Default is ``'random'`` (`random layout
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.random_layout.html>`__).
    :param nrows: Number of rows in the figure. Default is ``1``.
    :param ncols: Number of columns in the figure. Default is ``None``.
    :param names: Whether to show the graph names as titles. Default is ``None``.

        * If ``None``, shows the snapshot index as title.

        * If ``True``, show the graph names as title.

        * If ``False``, does not show the graph names.

    :param suptitle: Centered suptitle of the figure. Optional.
    :param temporal_opts: List or dictionary with drawing options for snapshots. Optional.
    :param layout_opts: List or dictionary with layout options for each graph. Optional.
    :param draw_opts: Additional drawing options for all graphs. Optional.
    """
    layout = getattr(nx, f"{layout.replace('_layout', '')}_layout", None)

    if plt is None:
        raise ModuleNotFoundError("This function requires 'matplotlib' to be installed.")

    assert pos is None or type(pos) == dict,\
        "Argument `pos` must be a dictionary or None."

    assert nrows > 0,\
        "Argument `nrows` must be a positive integer."

    assert ncols is None or ncols > 0,\
        "Argument `ncols` must be a positive integer or None."

    assert layout is not None,\
        "Argument `layout` must be a valid NetworkX layout algorithm. Available options: "\
        f"{[f for f in dir(nx) if f.endswith('_layout')]}"

    assert figsize is None or type(figsize) == tuple,\
        "Argument `figsize` must be a tuple or None."

    assert suptitle is None or type(suptitle) == str,\
        "Argument `suptitle` must be a string or None."

    assert layout_opts is None or type(layout_opts) in (list, dict),\
        "Argument `layout_opts` must be a dictionary or a list."

    assert type(layout_opts) != list or len(layout_opts) == len(TG),\
        "Argument `layout_opts` must have the same length as `TG`."

    assert temporal_opts is None or type(temporal_opts) in (list, dict),\
        "Argument `temporal_opts` must be a dictionary or a list."

    assert type(temporal_opts) != list or len(temporal_opts) == len(TG),\
        "Argument `temporal_opts` must have the same length as `TG`."

    if type(TG) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
        TG = [TG]  # Allows a single graph to be passed as input.

    if layout_opts is None:
        layout_opts = {}
    elif type(layout_opts) == list:
        layout_opts = {t: {} for t in range(len(TG))}

    if temporal_opts is None:
        temporal_opts = {}
    elif type(temporal_opts) == list:
        temporal_opts = {t: {} for t in range(len(TG))}

    fig, ax = plt.subplots(nrows=nrows,
                           ncols=ncols or len(TG) or 1,
                           figsize=figsize,
                           constrained_layout=True)

    i, j = 0, 0
    for t in range(len(TG)):
        ax_ = ax if len(TG) == 1 else ax[t] if nrows == 1 else ax[i, j]

        nx.draw(TG[t],
                ax=ax_,
                pos=pos or layout(TG[t], **layout_opts.get(t, {})),
                **{**DRAW_OPTS, **draw_opts, **temporal_opts.get(t, {})})

        if names is not False:
            name = (TG.names[t] or TG[t].name) if names is True else None
            ax_.set_title("" if len(TG) == 1 else name or f"$t$ = {t}")

        j += 1
        if ncols and j % ncols == 0:
            j = 0
            i += 1

    if suptitle:
        plt.suptitle(suptitle)

    plt.close()

    return fig
