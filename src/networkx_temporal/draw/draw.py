from typing import Optional, Union

import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from ..typing import TemporalGraph, Figure

FIG_OPTS = {
    "constrained_layout": True,
}

DRAW_OPTS = {
    "arrows": True,
    "edge_color": "#00000050",
    "node_color": "#aaa",
    "node_size": 250,
    "with_labels": True
}


def draw(
    graph: Union[TemporalGraph, nx.Graph, list],
    pos: Optional[dict] = None,
    layout: Optional[str] = "random",
    names: Optional[Union[list, bool]] = None,
    edge_labels: Optional[bool] = False,
    figsize: tuple = (3, 3),
    nrows: int = 1,
    ncols: Optional[int] = None,
    borders: Optional[bool] = False,
    suptitle: Optional[Union[str, bool]] = None,
    fig_opts: Optional[dict] = None,
    layout_opts: Optional[Union[list, dict]] = None,
    temporal_opts: Optional[Union[list, dict]] = None,
    **kwargs
) -> Figure:
    """
    Wrapper method around `NetworkX's draw
    <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
    function.

    Returns a `Matplotlib Figure <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__
    with temporal graph snapshots as subplots. Node positions can be provided as a dictionary or
    computed using one of `NetworkX's layout algorithms
    <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__.
    Further customization is possible by setting ``fig_opts``, ``layout_opts``, ``temporal_opts``,
    and ``kwargs``.

    Requires additional libraries to be installed, available from the ``draw`` extra:

    .. code-block:: bash

        $ pip install 'networkx-temporal[draw]'

    .. important::

        This function simply calls `NetworkX's draw
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
        in the backend and returns a `matplotlib Figure
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__ with
        temporal graph snapshots as subplots. It does not scale well to large graphs, which usually
        require more sophisticated approaches or specialized visualization tools.

    .. rubric:: Example

    Create a temporal directed graph and plot its snapshots using the `Kamada-Kawai
    <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html>`__
    algorithm:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalDiGraph()  # TG = tx.temporal_graph(directed=True, multigraph=False)
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
       >>>     ("c", "a", {"time": 4}),
       >>>     ("f", "c", {"time": 5}),
       >>>     ("a", "f", {"time": 5}),
       >>>     ("f", "c", {"time": 5}),
       >>> ])
       >>>
       >>> TG = TG.slice(attr="time")
       >>>
       >>> fig = tx.draw(TG,
       >>>               layout="kamada_kawai",
       >>>               figsize=(6, 4),
       >>>               nrows=2,
       >>>               ncols=3,
       >>>               borders=True,
       >>>               suptitle=True)
       >>>
       >>> # Save figure to file.
       >>> # fig.savefig("figure.png")
       >>>
       >>> fig

    .. image:: ../../figure/example/fig-draw.png

    |

    .. seealso::

        - The `drawing documentation
          <https://networkx.org/documentation/stable/reference/drawing.html>`__ from NetworkX
          for more information on plotting graphs.
        - The `Examples → Basic operations → Slice temporal graph
          <https://networkx-temporal.readthedocs.io/en/latest/examples/basics.html#slice-temporal-graph>`__
          and `Examples → Community detection
          <https://networkx-temporal.readthedocs.io/en/latest/examples/community.html>`__
          pages for more examples using this function to plot simple temporal graphs.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.TemporalGraph`, a static
        graph, or a list of static graphs from NetworkX as input.
    :param pos: Dictionary with nodes as keys and positions as values, e.g.,
        ``{'node': (0.19813, 0.74631), ...}``. Optional.
    :param layout: The `graph layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        to calculate node positions with, when ``pos`` is not provided. Optional.
        Default is ``'random'``.
    :param names: Whether to show the graph :attr:`~networkx_temporal.TemporalGraph.names` property
        as titles. Default is ``None``.

        * If ``None``, shows the snapshot index as title.

        * If ``True``, show the graph names as title.

        * If ``False``, does not show titles.

        * If a ``list``, shows the values in it as titles.

    :param edge_labels: Attribute to use as edge labels. Optional.
    :param figsize: Tuple with the dimensions of the figure. Default is ``(3, 3)``.
    :param nrows: Number of rows in the figure. Default is ``1``.
    :param ncols: Number of columns in the figure. Default is ``None``.
    :param borders: Draw borders around subplots. Default is ``False``.
    :param suptitle: Centered suptitle of the figure. If ``True``, uses the temporal graph
        :attr:`~networkx_temporal.TemporalGraph.name` property or its string representation. Optional.
    :param fig_opts: Additional `subplots
       <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html>`__ options. Optional.
    :param layout_opts: Additional layout algorithm options. Optional.

       * If a ``list``, consider each element as options for a snapshot.

       * If a ``dict``, consider it as options for all snapshots.

    :param temporal_opts: Additional drawing options per snapshot. Optional.

       * If a ``list``, consider each element as options for a snapshot.

       * If a ``dict``, keys are snapshot indices and values are options.

    :param kwargs: Additional drawing options for all graphs. Optional.
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
    assert suptitle is None or type(suptitle) in (str, bool),\
        "Argument `suptitle` must be a string or a boolean."
    assert layout_opts is None or type(layout_opts) in (list, dict),\
        "Argument `layout_opts` must be a dictionary or a list."
    assert type(layout_opts) != list or len(layout_opts) == len(graph),\
        "Argument `layout_opts` must have the same length as `graph`."
    assert temporal_opts is None or type(temporal_opts) in (list, dict),\
        "Argument `temporal_opts` must be a dictionary or a list."
    assert type(temporal_opts) != list or len(temporal_opts) == len(graph),\
        "Argument `temporal_opts` must have the same length as `graph`."

    if type(graph) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
        graph = [graph]  # Allows a single graph to be passed as input.

    if not nrows:
        nrows = len(graph) if ncols == 1 else 1
    if not ncols:
        ncols = len(graph) if nrows == 1 else 1

    if type(layout_opts) == list:
        layout_opts = {t: layout_opts[t] for t in range(len(graph))}
    if type(temporal_opts) == list:
        temporal_opts = {t: temporal_opts[t] for t in range(len(graph))}

    fig, ax = plt.subplots(nrows=nrows,
                           ncols=ncols,
                           figsize=figsize,
                           **{**FIG_OPTS, **(fig_opts or {})})

    i, j = 0, 0
    for t in range(len(graph)):
        ax_ = ax if len(graph) == 1 else ax[t] if nrows == 1 or ncols == 1 else ax[i, j]
        pos_ = pos or layout(graph[t], **((layout_opts or {}).get(t, layout_opts) or {}))
        opts_ = {**DRAW_OPTS, **kwargs, **((temporal_opts or {}).get(t, temporal_opts) or {})}

        draw = getattr(nx, "draw_networkx" if borders else "draw")
        draw(graph[t], ax=ax_, pos=pos_, **opts_)

        if edge_labels:
            edge_labels_ = {(u, v, k): x for u, v, k, x in graph[t].edges(data=edge_labels, keys=True)}\
                           if graph[t].is_multigraph() else\
                           {(u, v): x for u, v, x in graph[t].edges(data=edge_labels)}

            nx.draw_networkx_edge_labels(graph[t],
                                         pos=pos_,
                                         edge_labels=edge_labels_,
                                         font_color=opts_.get("edge_color"))

        if names is False:
            title = None
        elif names is None:
            title = f"$t$ = {t}" if len(graph) > 1 else None
        elif names is True:
            title = graph.names[t] if hasattr(graph, "names") else graph[t].name
        elif type(names) == list:
            title = names[t]

        ax_.set_title(title)

        j += 1
        if ncols and j % ncols == 0:
            j = 0
            i += 1

    if suptitle:
        suptitle = graph.name or str(graph).replace("t=", "$t$=") if suptitle is True else suptitle
        plt.suptitle(suptitle)

    plt.close()

    return fig
