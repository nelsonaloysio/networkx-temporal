from typing import Callable, Optional, Sequence, Union

import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from ..graph import is_temporal_graph
from ..typing import Figure, TemporalGraph


NODE_OPTS = {
    "edgecolors": "black",
    "node_color": "tab:red",
    "node_size": 250,
}

EDGE_OPTS = {
    "arrows": True,
    "edge_color": "black",
}

NODE_LABEL_OPTS = {
    "font_color": "whitesmoke",
}

EDGE_LABEL_OPTS = {
    "font_color": "black",
}


def draw_networkx(
    graph: Union[TemporalGraph, nx.Graph, list],
    pos: Optional[Union[list, dict]] = None,
    layout: Optional[Union[str, Callable]] = 'random',
    nrows: Optional[int] = None,
    ncols: Optional[int] = None,
    fig: Optional[Figure] = None,
    figsize: tuple = (3, 3),
    constrained_layout: bool = True,
    border: bool = False,
    suptitle: Optional[Union[str, bool]] = None,
    names: Optional[Union[list, bool]] = None,
    labels: Optional[Union[str, dict, bool]] = True,
    edge_labels: Optional[Union[str, dict, bool]] = False,
    node_opts: Optional[Union[list, dict]] = None,
    edge_opts: Optional[Union[list, dict]] = None,
    node_label_opts: Optional[Union[list, dict]] = None,
    edge_label_opts: Optional[Union[list, dict]] = None,
    layout_opts: Optional[Union[list, dict]] = None,
    **opts
) -> Figure:
    """
    Returns a `Matplotlib Figure <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__
    using `NetworkX <https://networkx.org/documentation/stable/reference/drawing.html>`_ to plot
    temporal graph snapshots as subplots.

    This function accepts global or specific options for nodes, edges, labels, and layout algorithms.
    Arguments prefixed with ``temporal_`` expect a dictionary of dictionaries (indexed by snapshot key)
    to be applied on a per snapshot basis, overriding static options. Element-specific options (e.g.,
    ``node_opts``) override global ``opts`` and allow greater control over the drawing process.

    Requires additional libraries to be installed, available from the ``draw`` extra:

    .. code-block:: bash

        $ pip install 'networkx-temporal[draw]'

    .. important::

        This function simply calls `NetworkX draw
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html>`__
        in the backend and returns a `matplotlib Figure
        <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__ with
        temporal graph snapshots as subplots. It does not scale well to large graphs, which usually
        require more sophisticated approaches or specialized visualization tools.

    .. rubric:: Example

    Create a temporal directed graph and plot its snapshots using the `Kamada-Kawai
    <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html>`__
    algorithm, coloring nodes by the time (snapshot index) of their first appearance in the network:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> import matplotlib.pyplot as plt
       >>> import matplotlib.patches as mpatches
       >>>
       >>> colors = plt.cm.tab10.colors
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
       >>> node_color = {t: [colors[TG.index_node(node)[0]] for node in nodes]
       >>>               for t, nodes in enumerate(TG.nodes())}
       >>>
       >>> fig = tx.draw(TG,
       >>>               layout="kamada_kawai",
       >>>               temporal_node_color=node_color,
       >>>               figsize=(6, 4),
       >>>               nrows=2,
       >>>               ncols=3,
       >>>               border=True,
       >>>               suptitle=True)
       >>>
       >>> handles = [mpatches.Patch(color=colors[i], label=f"$t$ = {i}")
       >>>            for i in range(1+max([TG.index_node(n)[0] for n in TG.temporal_nodes()]))]
       >>>
       >>> fig.legend(handles=handles, ncols=4, bbox_to_anchor=(0.5, -0.15),
       >>>            loc="lower center", title="Time of first node appearance")
       >>>
       >>> # Save figure to file.
       >>> # fig.savefig("figure.png")
       >>>
       >>> fig

    .. image:: ../../figure/example/fig-draw.png

    .. seealso::

        - The drawing `documentation
          <https://networkx.org/documentation/stable/reference/drawing.html>`__
          and `gallery
          <https://networkx.org/documentation/stable/auto_examples/index.html#drawing>`__
          from NetworkX for more details and examples.
        - The `Examples → Basic operations → Slice temporal graph
          <../examples/basics.html#slice-temporal-graph>`__
          and `Examples → Community detection
          <../examples/community.html>`__
          pages for more examples using this function to plot simple temporal graphs.
        - The :func:`~networkx_temporal.drawing.networkx.draw_networkx_nodes`,
          :func:`~networkx_temporal.drawing.networkx.draw_networkx_edges`,
          :func:`~networkx_temporal.drawing.networkx.draw_networkx_labels`, and
          :func:`~networkx_temporal.drawing.networkx.draw_networkx_edge_labels`
          functions for drawing specific graph elements.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.graph.TemporalGraph`, a
        static graph, or a list of static graphs from NetworkX as input.
    :param pos: Dictionary or list of dictionaries with nodes as keys and positions as values, e.g.,
        ``{'node': (0.19813, 0.74631), ...}``.
    :param layout: A callable or string with a `layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        from NetworkX to calculate node positions with. Default is ``'random'``.
    :param nrows: Number of rows in the figure. Optional.
    :param ncols: Number of columns in the figure. Optional.
    :param fig: Matplotlib figure object. Optional.
    :param figsize: Tuple with the dimensions of the figure. Default is ``(3, 3)``.
    :param constrained_layout: Use a `constrained layout
        <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html>`__.
        Default is ``True``.
    :param border: Draw border around subplots. Default is ``False``.
    :param suptitle: Centered suptitle of the figure. If ``True``, uses the temporal graph
        :attr:`~networkx_temporal.graph.TemporalGraph.name` property or its string representation. Optional.
    :param names: Whether to show the graph :attr:`~networkx_temporal.graph.TemporalGraph.names` property
        as titles. Default is ``None``.

        * If ``None``, shows the snapshot index as title.

        * If ``True``, show the graph names as title.

        * If ``False``, does not show titles.

        * If a ``list``, shows the values in it as titles.
    :param labels: A string, dictionary, or boolean to control node labels.

        * If a ``str``, use it as the attribute name to show as labels.

        * If a ``dict``, keys are node indices and values are labels.

        * If a ``bool``, whether to show labels or not. Default is ``True``.

    :param edge_labels: A string, dictionary, or boolean to control edge labels.

        * If a ``str``, use it as the attribute name to show as labels.

        * If a ``dict``, keys are edge indices and values are labels.

        * If a ``bool``, whether to show labels or not. Default is ``False``.

    :param node_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        additional options for drawing nodes. Optional.
    :param edge_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        additional options for drawing edges. Optional.
    :param node_label_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        additional options for nodes labels. Optional.
    :param edge_label_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        additional options for edge labels. Optional.
    :param layout_opts: Dictionary or list of dictionaries (one per snapshot) with
        additional options for the ``layout`` algorithm. Optional.
    :param opts: Additional drawing options passed to each drawing
        or layout algorithm functions. Optional. Overriden by
        ``node_opts``, ``edge_opts``, ``node_label_opts``, ``edge_label_opts``,
        and ``layout_opts`` if provided.
    """
    if not callable(layout):
        layout = getattr(nx, f"{(layout or 'random').replace('_layout', '')}_layout", None)

    assert pos is None or type(pos) in (list, dict),\
        "Argument `pos` must be a dictionary or a list of dictionaries."
    assert pos or layout is not None,\
        "Argument `layout` must be a string with a valid NetworkX layout algorithm."\
        f"Available choices: {[f for f in dir(nx) if f.endswith('_layout')]}"
    assert nrows is None or nrows > 0,\
        "Argument `nrows` must be a positive integer."
    assert ncols is None or ncols > 0,\
        "Argument `ncols` must be a positive integer or None."
    assert figsize is None or type(figsize) == tuple,\
        "Argument `figsize` must be a tuple."
    assert suptitle is None or type(suptitle) in (str, bool),\
        "Argument `suptitle` must be a string or a boolean."

    # Allow a single graph to be passed as input.
    if not is_temporal_graph(graph):
        graph = [graph]

    # Decide number of columns and rows if not provided.
    if not nrows:
        nrows = len(graph) if ncols == 1 else 1
    if not ncols:
        ncols = len(graph) if nrows == 1 else 1

    # Create figure and axes if not provided.
    if fig is None:
        fig, ax = plt.subplots(nrows=nrows,
                               ncols=ncols,
                               figsize=figsize,
                               constrained_layout=constrained_layout)
    else:
        ax = fig.axes

    i, j = 0, 0
    for t in range(len(graph)):
        ax_ = ax if nrows == 1 and ncols == 1 else ax[t] if nrows == 1 or ncols == 1 else ax[i, j]

        # Get or compute node positions.
        pos_ = pos if type(pos) == dict else pos[t] if type(pos) == list else layout(
            graph[t],
            **_get_opts(opts, layout_opts, t=t, sig=layout)
        )

        # Draw graph elements.
        if opts.get("with_nodes", labels):
            nx.draw_networkx_nodes(
                graph[t], pos=pos_, ax=ax_,
                **_get_opts(NODE_OPTS, opts, node_opts, t=t, sig=nx.draw_networkx_nodes)
            )

        if opts.get("with_edges", labels):
            nx.draw_networkx_edges(
                graph[t], pos=pos_, ax=ax_,
                **_get_opts(EDGE_OPTS, opts, edge_opts, t=t, sig=nx.draw_networkx_edges)
            )

        # Draw node labels.
        if opts.get("with_labels", labels):
            nx.draw_networkx_labels(
                graph[t], pos=pos_, ax=ax_,
                **_get_opts(NODE_LABEL_OPTS, opts, node_label_opts, t=t, sig=nx.draw_networkx_labels),
                **_get_node_labels(graph[t], labels)
            )

        # Draw edge labels.
        if opts.get("with_edge_labels", edge_labels):
            nx.draw_networkx_edge_labels(
                graph[t], pos=pos_, ax=ax_,
                **_get_opts(EDGE_LABEL_OPTS, opts, edge_label_opts, t=t, sig=nx.draw_networkx_edge_labels),
                **_get_edge_labels(graph[t], edge_labels)
            )

        # Set graph borders.
        if border is True:
            ax_.set_axis_on()
        else:
            ax_.set_axis_off()

        # Set graph titles.
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


def draw_networkx_nodes(*args, **kwargs):
    """
    Draw only temporal nodes from a :class:`~networkx_temporal.graph.TemporalGraph` object.

    .. seealso::

        The `draw_networkx_nodes
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_nodes.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("node_opts", {}))
    kwargs.update({"with_edges": False, "with_labels": False, "with_edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_edges(*args, **kwargs):
    """
    Draw only temporal edges from a :class:`~networkx_temporal.graph.TemporalGraph` object.

    .. seealso::

        The `draw_networkx_edges
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_edges.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("edge_opts", {}))
    kwargs.update({"with_nodes": False, "with_labels": False, "with_edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_labels(*args, **kwargs):
    """
    Draw only temporal node labels from a :class:`~networkx_temporal.graph.TemporalGraph` object.

    .. seealso::

        The `draw_networkx_labels
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_labels.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("node_label_opts", {}))
    kwargs.update({"with_nodes": False, "with_edges": False, "with_edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_edge_labels(*args, **kwargs):
    """
    Draw only temporal edge labels from a :class:`~networkx_temporal.graph.TemporalGraph` object.

    .. seealso::

        The `draw_networkx_edge_labels
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_edge_labels.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("edge_label_opts", {}))
    kwargs.update({"with_nodes": False, "with_edges": False, "with_labels": False})
    return draw_networkx(*args, **kwargs)


def _get_node_labels(G, attr: Optional[Union[str, dict]] = None, key: str = "labels") -> dict:
    """
    Helper function to get node attributes in a graph.

    :param G: Graph object.
    :param str attr: Dictionary or node attribute to use as label. Optional.
    :param key: Dictionary key name. Default is ``'labels'``.
    """
    if type(attr) == str:
        return {key: {n: x for n, x in G.nodes(data=attr)}}

    if type(attr) == dict:
        return {key: attr}

    return {}


def _get_edge_labels(G, attr: Optional[Union[str, dict]] = None, key: str = "edge_labels") -> dict:
    """
    Helper function to get edge attributes in a graph.

    :param G: Graph object.
    :param str attr: Dictionary or edge attribute to use as label. Optional.
    :param key: Dictionary key name. Default is ``'edge_labels'``.
    """
    if type(attr) == str:
        if G.is_multigraph():
            return {key: {(u, v, k): x for u, v, k, x in G.edges(data=attr, keys=True)}}
        return {key: {(u, v): x for u, v, x in G.edges(data=attr)}}

    if type(attr) == dict:
        return {key: attr}

    return {}


def _get_opts(*opts: Sequence[Union[dict, list]], t: Optional[int] = None, sig: Optional[Callable] = None) -> dict:
    """
    Helper function to get options per snapshot.

    :param dict opts: Dictionary or list of dictionaries with keyword arguments.
    :param int t: Snapshot index. Optional.
    :param Callable sig: Signature of the function to filter keyword arguments. Optional.
    """
    options = {}

    list(options.update({k.split("temporal_")[-1]: v[t]} if k.startswith("temporal_") else {k: v})
         for opts in opts for k, v in (opts or {}).items())

    return {k: v for k, v in options.items() if sig is None or k in sig.__code__.co_varnames}
