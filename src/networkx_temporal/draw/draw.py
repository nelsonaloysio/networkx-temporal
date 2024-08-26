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
    nrows: int = 1,
    ncols: Optional[int] = None,
    names: Optional[Union[list, bool]] = None,
    edge_labels: Optional[bool] = False,
    suptitle: Optional[str] = None,
    plot_opts: Optional[dict] = None,
    temporal_opts: Optional[Union[list, dict]] = None,
    layout_opts: Optional[Union[list, dict]] = None,
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

    .. important::

        This function simply calls `NetworkX's draw
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
        in the backend and returns a `matplotlib Figure
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__ with
        temporal graph snapshots as subplots. It does not scale well to large graphs, which usually
        require more sophisticated approaches or specialized visualization tools.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.TemporalDiGraph()
        >>> # TG = tx.temporal_graph(directed=True, multigraph=False)
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

    .. seealso::

        - The `drawing documentation
          <https://networkx.org/documentation/stable/reference/drawing.html>`__ from NetworkX
          for more information on plotting graphs.
        - The `Examples: Slice temporal graph
          <https://networkx-temporal.readthedocs.io/en/latest/examples/basics.html#slice-temporal-graph>`__
          and `Examples: Community detection
          <https://networkx-temporal.readthedocs.io/en/latest/examples/community.html>`__
          pages from the documentation for more snippets using this function to draw temporal graphs.

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

        * If ``False``, does not show titles.

        * If a ``list``, shows the values in it as titles.

    :param suptitle: Centered suptitle of the figure. Optional.
    :param plot_opts: Additional options for the figure. Optional.
    :param temporal_opts: List or dictionary with drawing options for snapshots. Optional.
    :param layout_opts: List or dictionary with layout options for each graph. Optional.
    :param draw_opts: Additional drawing options for all graphs. Optional.
    """
    layout = getattr(nx, f"{layout.replace('_layout', '')}_layout", None)

    if plt is None:
        raise ModuleNotFoundError(
            f"Package 'matplotlib' is not installed. Please install it and try again."
        )

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

    if type(layout_opts) == list:
        layout_opts = {t: layout_opts[t] for t in range(len(TG))}

    if type(temporal_opts) == list:
        temporal_opts = {t: temporal_opts[t] for t in range(len(TG))}

    fig, ax = plt.subplots(nrows=nrows,
                           ncols=ncols or len(TG) or 1,
                           figsize=figsize,
                           constrained_layout=True,
                           **(plot_opts or {}))

    i, j = 0, 0
    for t in range(len(TG)):
        ax_ = ax if len(TG) == 1 else ax[t] if nrows == 1 else ax[i, j]
        pos_ = pos or layout(TG[t], **(layout_opts or {}).get(t, {}))
        opts_ = {**DRAW_OPTS, **draw_opts, **(temporal_opts or {}).get(t, {})}

        nx.draw(TG[t], ax=ax_, pos=pos_, **opts_)

        if edge_labels:
            edge_labels_ = {(u, v, k): x for u, v, k, x in TG[t].edges(data=edge_labels, keys=True)}\
                           if TG[t].is_multigraph() else\
                           {(u, v): x for u, v, x in TG[t].edges(data=edge_labels)}

            nx.draw_networkx_edge_labels(TG[t],
                                         pos=pos_,
                                         edge_labels=edge_labels_,
                                         font_color=opts_.get("edge_color"))

        if names is False:
            title = None
        elif names is None:
            title = f"$t$ = {t}" if len(TG) > 1 else None
        elif names is True:
            title = TG.names[t] if hasattr(TG, "names") else TG[t].name
        elif type(names) == list:
            title = names[t]

        ax_.set_title(title)

        j += 1
        if ncols and j % ncols == 0:
            j = 0
            i += 1

    plt.suptitle(suptitle)
    plt.close()

    return fig
