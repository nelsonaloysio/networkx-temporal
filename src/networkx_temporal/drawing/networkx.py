from typing import Callable, Optional, Sequence, Union

import networkx as nx
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from .layout import _layout_func
from ..classes.types import is_temporal_graph
from ..typing import Figure, StaticGraph, TemporalGraph

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
    TG: Union[TemporalGraph, StaticGraph],
    pos: Optional[Union[list, dict]] = None,
    layout: Optional[Union[str, Callable]] = 'random',
    nrows: Optional[int] = None,
    ncols: Optional[int] = None,
    fig: Optional[Figure] = None,
    ax: Optional[int] = None,
    figsize: tuple = (3, 3),
    constrained_layout: bool = True,
    border: bool = False,
    title: Optional[Union[str, list, bool]] = None,
    suptitle: Optional[Union[str, bool]] = None,
    nodes: Optional[bool] = True,
    edges: Optional[bool] = True,
    labels: Optional[Union[str, dict, bool]] = True,
    edge_labels: Optional[Union[str, dict, bool]] = False,
    node_opts: Optional[Union[list, dict]] = None,
    edge_opts: Optional[Union[list, dict]] = None,
    node_label_opts: Optional[Union[list, dict]] = None,
    edge_label_opts: Optional[Union[list, dict]] = None,
    layout_opts: Optional[Union[list, dict]] = None,
    **opts
) -> Figure:
    """ Plot temporal graph snapshots with NetworkX.
    Returns a `Matplotlib Figure <https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html>`__
    with subplots.

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

    .. note::

        While the parameters ``nodes`` and ``edges`` control only the visibility of these elements,
        the parameters ``labels`` and ``edge_labels`` also allow passing a string, dictionary,
        or list of such types to control the content of the node and edge labels shown in the plot,
        respectively.

    .. rubric:: Example

    Create a temporal directed graph and plot its snapshots using the `Kamada-Kawai
    <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.kamada_kawai_layout.html>`__
    algorithm, coloring nodes by the time (snapshot index) of their first appearance in the network:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>> import matplotlib.pyplot as plt
        >>> import matplotlib.patches as mpatches
        >>>
        >>> colors = plt.cm.tab10.colors
        >>>
        >>> TG = tx.TemporalDiGraph()
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
        >>> # Plot temporal graph snapshots with node colors by time of first appearance.
        >>> temporal_node_color = {t: [colors[TG.index_node(node)[0]] for node in nodes]
        >>>                        for t, nodes in enumerate(TG.nodes())}
        >>>
        >>> fig = tx.draw(TG,
        >>>               layout="kamada_kawai",
        >>>               temporal_node_color=temporal_node_color,
        >>>               figsize=(6, 4),
        >>>               nrows=2,
        >>>               ncols=3,
        >>>               border=True,
        >>>               suptitle=True)
        >>>
        >>> # Add legend to figure.
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

    .. image:: ../../assets/figure/drawing/draw_networkx.png

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
        - The :func:`~networkx_temporal.drawing.draw_networkx_nodes`,
          :func:`~networkx_temporal.drawing.draw_networkx_edges`,
          :func:`~networkx_temporal.drawing.draw_networkx_labels`, and
          :func:`~networkx_temporal.drawing.draw_networkx_edge_labels`
          functions for drawing specific graph elements.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param pos: Dictionary or list of dictionaries with nodes as keys and positions as values, e.g.,
        ``{'node': (0.19813, 0.74631), ...}``.
    :param layout: A callable or string with a `layout algorithm
        <https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout>`__
        from NetworkX to calculate node positions with. Default is ``'random'``.
    :param nrows: Number of rows in the figure. Optional.
    :param ncols: Number of columns in the figure. Optional.
    :param fig: Matplotlib figure object. Optional.
    :param ax: Axes index of subplot to draw the graph on. Optional.
    :param figsize: Tuple with the dimensions of the figure. Default is ``(3, 3)``.
    :param constrained_layout: Use a `constrained layout
        <https://matplotlib.org/stable/users/explain/axes/constrainedlayout_guide.html>`__.
        Default is ``True``.
    :param border: Draw border around subplots. Default is ``False``.
    :param suptitle: Centered figure's `super title <https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html>`__.
        Default is ``None``.

        * If ``True``, use the graph's :attr:`~networkx_temporal.classes.TemporalGraph.name`
          property or its string representation.

        * If ``False`` or ``None``, does not show a super title.

        * If a ``str``, use it as the super title.
    :param title: Centered figure's title. Default is ``None``.

        * If ``None``, show the snapshot index as title.

        * If ``True``, show the graph ``name`` as title.

        * If ``False``, does not show titles.

        * If a ``list``, passed values are used as titles.

        * If a ``str``, passed value is used as title.
    :param nodes: Whether to draw nodes. Default is ``True``.
    :param edges: Whether to draw edges. Default is ``True``.
    :param labels: A string, dictionary, or boolean to control node labels.
        Default is ``True``.

        * If a ``str``, use it as the attribute name to show as labels.

        * If a ``dict``, keys are node indices and values are labels.

        * If a ``bool``, whether to show labels or not.

    :param edge_labels: A string, dictionary, or boolean to control edge labels.
        Default is ``False``.

        * If a ``str``, use it as the attribute name to show as labels.

        * If a ``dict``, keys are edge indices and values are labels.

        * If a ``bool``, whether to show labels or not.

    :param node_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        options to set :func:`~networkx_temporal.draw.networkx.nx.draw_networkx_nodes`.
    :param edge_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        options to set :func:`~networkx_temporal.draw.networkx.nx.draw_networkx_edges`.
    :param node_label_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        options to set :func:`~networkx_temporal.draw.networkx.nx.draw_networkx_labels`.
    :param edge_label_opts: Dictionary or dictionary of dictionaries (one per snapshot) with
        options to set :func:`~networkx_temporal.draw.networkx.nx.draw_networkx_edge_labels`.
    :param layout_opts: Dictionary or list of dictionaries (one per snapshot) with
        additional options for the ``layout`` algorithm. Optional.
    :param opts: Additional drawing options passed to each drawing
        or layout algorithm functions. Optional. Overriden by
        ``node_opts``, ``edge_opts``, ``node_label_opts``, ``edge_label_opts``,
        and ``layout_opts`` if provided.
    """
    if plt is None:
        raise ImportError(
            "Matplotlib is required to use the drawing module. "
            "Please install the package with the 'draw' extra: "
            "`pip install 'networkx-temporal[draw]'`"
        )

    if type(layout) == str:
        layout = _layout_func(layout)

    if pos is None and layout is None:
        raise ValueError(
            "Argument `layout` expects a str with a valid NetworkX layout algorithm, "
            f"choices: {[f for f in dir(nx) if f.endswith('_layout')]}"
        )
    if nodes is not None and type(nodes) != bool:
        raise TypeError("Argument `nodes` must be a boolean.")
    if edges is not None and type(edges) != bool:
        raise TypeError("Argument `edges` must be a boolean.")
    if labels is not None and type(labels) not in (str, dict, bool):
        raise TypeError("Argument `labels` must be a string, dictionary, or boolean.")
    if edge_labels is not None and type(edge_labels) not in (str, dict, bool):
        raise TypeError("Argument `edge_labels` must be a string, dictionary, or boolean.")
    if pos is not None and type(pos) not in (list, dict):
        raise TypeError("Argument `pos` must be a dictionary or a list of dictionaries.")
    if not (nrows is None or type(nrows) == int and nrows > 0):
        raise ValueError("Argument `nrows` must be a positive integer.")
    if not (ncols is None or type(ncols) == int and ncols > 0):
        raise ValueError("Argument `ncols` must be a positive integer or None.")
    if figsize is not None and type(figsize) != tuple:
        raise TypeError("Argument `figsize` must be a tuple.")
    if suptitle is not None and type(suptitle) not in (str, bool):
        raise TypeError("Argument `suptitle` must be a string or a boolean.")

    # Allow a single graph to be passed as input.
    if not is_temporal_graph(TG):
        TG = [TG]

    # Decide number of columns and rows if not provided.
    if not nrows:
        nrows = len(TG) if ncols == 1 else 1
    if not ncols:
        ncols = len(TG) if nrows == 1 else 1

    # Create figure and axes if not provided.
    if fig is None:
        fig, ax = plt.subplots(nrows=nrows,
                               ncols=ncols,
                               figsize=figsize,
                               constrained_layout=constrained_layout)
    else:
        ax = fig.axes[ax] if type(ax) == int else fig.axes[0] if len(TG) == 1 else ax

    i, j = 0, 0
    for t in range(len(TG)):
        ax_ = ax if nrows == ncols == 1 else ax[t] if nrows == 1 or ncols == 1 else ax[i, j]

        # Get or compute node positions.
        pos_ = pos if type(pos) == dict else pos[t] if type(pos) == list else layout(
            TG[t],
            **_get_opts(opts, layout_opts, t=t, sig=layout)
        )
        # Draw graph elements with defaults overridden by opts and element-specific options.
        if nodes is not False:
            nx.draw_networkx_nodes(
                TG[t], pos=pos_, ax=ax_,
                **_get_opts(NODE_OPTS, opts, node_opts, t=t, sig=nx.draw_networkx_nodes)
            )
        if edges is not False:
            nx.draw_networkx_edges(
                TG[t], pos=pos_, ax=ax_,
                **_get_opts(EDGE_OPTS, opts, edge_opts, t=t, sig=nx.draw_networkx_edges)
            )
        if labels is not False and opts.get("with_labels", True):
            nx.draw_networkx_labels(
                TG[t], pos=pos_, ax=ax_,
                **_get_opts(NODE_LABEL_OPTS, opts, node_label_opts, t=t, sig=nx.draw_networkx_labels),
                **_get_node_labels(TG[t], labels)
            )
        if edge_labels is not False:
            nx.draw_networkx_edge_labels(
                TG[t], pos=pos_, ax=ax_,
                **_get_opts(EDGE_LABEL_OPTS, opts, edge_label_opts, t=t, sig=nx.draw_networkx_edge_labels),
                **_get_edge_labels(TG[t], edge_labels)
            )

        # Set graph borders.
        if border is True:
            ax_.set_axis_on()
        else:
            ax_.set_axis_off()

        # Set graph titles.
        if title is False or opts.get("names", None) is False:
            title_ = None
        elif title is True or opts.get("names", None):
            title_ = TG.names[t] if TG.names is not None else TG[t].name
        elif title is None:
            title_ = f"$t$ = {t}" if len(TG) > 1 else None
        elif type(title) == str:
            title_ = title
        elif type(title) == list:
            title_ = title[t]
        ax_.set_title(title_)

        j += 1
        if ncols and j % ncols == 0:
            j = 0
            i += 1

    if suptitle:
        suptitle = TG.name or str(TG).replace("t=", "$t$=") if suptitle is True else suptitle
        plt.suptitle(suptitle)

    plt.close()
    return fig


def draw_networkx_nodes(*args, **kwargs):
    """ Plot temporal nodes from a :class:`~networkx_temporal.classes.TemporalGraph`.

    .. seealso::

        The `draw_networkx_nodes
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_nodes.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("node_opts", {}))
    kwargs.update({"edges": False, "labels": False, "edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_edges(*args, **kwargs):
    """ Plot temporal edges from a :class:`~networkx_temporal.classes.TemporalGraph`.

    .. seealso::

        The `draw_networkx_edges
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_edges.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("edge_opts", {}))
    kwargs.update({"nodes": False, "labels": False, "edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_labels(*args, **kwargs):
    """ Plot temporal node labels from a :class:`~networkx_temporal.classes.TemporalGraph`.

    .. seealso::

        The `draw_networkx_labels
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_labels.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("node_label_opts", {}))
    kwargs.update({"nodes": False, "edges": False, "edge_labels": False})
    return draw_networkx(*args, **kwargs)


def draw_networkx_edge_labels(*args, **kwargs):
    """ Plot temporal edge labels from a :class:`~networkx_temporal.classes.TemporalGraph`.

    .. seealso::

        The `draw_networkx_edge_labels
        <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.networkx.draw_networkx_edge_labels.html>`__
        function from NetworkX for a list of accepted arguments.

    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :note: This function acts as a wrapper to the :func:`~draw_networkx` function.
    """
    kwargs.update(kwargs.pop("edge_label_opts", {}))
    kwargs.update({"nodes": False, "edges": False, "labels": False})
    return draw_networkx(*args, **kwargs)


def _get_node_labels(G, attr: Optional[Union[str, dict]] = None, key: str = "labels") -> dict:
    """ Helper function to get node attributes in a graph.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
    :param str attr: Dictionary or node attribute to use as label. Optional.
    :param key: Dictionary key name. Default is ``'labels'``.
    """
    if type(attr) == str:
        return {key: {n: x for n, x in G.nodes(data=attr)}}

    if type(attr) == dict:
        return {key: attr}

    return {}


def _get_edge_labels(G, attr: Optional[Union[str, dict]] = None, key: str = "edge_labels") -> dict:
    """ Helper function to get edge attributes in a graph.

    :param object G: :class:`~networkx_temporal.classes.TemporalGraph`
        or static NetworkX graph object.
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


def _get_opts(*opts: Sequence[Union[dict, list]], t: int, sig: Optional[Callable] = None) -> dict:
    """ Helper function to get options per snapshot.

    :param dict opts: Dictionary or list of dictionaries with keyword arguments.
    :param int t: Snapshot index. Optional.
    :param Callable sig: Signature of the function to filter keyword arguments. Optional.
    """
    options = {}

    list(options.update({k.split("temporal_")[-1]: v[t]} if k.startswith("temporal_") else {k: v})
         for opts in opts for k, v in (opts or {}).items())

    return {k: v for k, v in options.items() if sig is None or k in sig.__code__.co_varnames}
