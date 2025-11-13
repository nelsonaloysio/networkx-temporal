from __future__ import annotations

from typing import Any, Callable, Optional, Union

import pandas as pd

from ..typing import Literal, TemporalGraph


def slice(
    self: TemporalGraph,
    bins: Optional[int] = None,
    attr: Optional[Union[str, list, dict, pd.DataFrame, pd.Series]] = None,
    level: Optional[Literal["edge", "node", "source", "target"]] = None,
    axis: int = 0,
    qcut: bool = False,
    duplicates: Literal["raise", "drop"] = "raise",
    rank_first: Optional[bool] = None,
    sort: bool = True,
    names: bool = True,
    as_view: bool = True,
    fillna: Optional[Any] = None,
    apply_func: Optional[Callable[..., Any]] = None,
) -> TemporalGraph:
    """ Slices temporal graph into snapshots, returning a new temporal graph object.

    All node interactions are preserved when using this method. Note that the returned object may
    contain temporal node copies, if they interact with other nodes in different intervals.

    If ``attr`` is unset, the method will consider the order of appearance of edges or nodes, i.e.,
    ``rank_first=True``. If ``attr`` is set and ``bins`` is unset, the method will create as many
    snapshots as unique values found in the specified node- or edge-level ``attr`` attribute data.
    Alternatively, a list of 2-tuple ``intervals`` may be provided with custom time windows.

    .. hint::

        By default, `views
        <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
        of the original graph are returned to avoid memory overhead. If the resulting
        snapshots need to be modified, set ``as_view=False`` to return copies instead.

    .. rubric:: Example

    Slicing a temporal graph into two snapshots based on the edge-level ``time`` attribute:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalGraph()
       >>>
       >>> TG.add_edge("a", "b", time=0)
       >>> TG.add_edge("c", "b", time=1)
       >>>
       >>> TG = TG.slice(attr="time")
       >>> print(TG)

       TemporalGraph (t=2) with 3 nodes and 2 edges

    Calling this method from the returned object, now with ``bins=1``, will
    :func:`~networkx_temporal.classes.TemporalGraph.flatten` the graph:

    .. code-block:: python

       >>> TG = TG.slice(bins=1)
       >>> print(TG)

       TemporalGraph (t=1) with 3 nodes and 2 edges

    Note that a :class:`~networkx_temporal.classes.TemporalMultiGraph` or
    :class:`~networkx_temporal.classes.TemporalMultiDiGraph` object is required to store multiple
    edges among pairs and allow many interactions between the same nodes.

    .. seealso::

        The
        `Examples → Basic Operations → Slice temporal graph
        <../examples/basics.html#slice-temporal-graph>`__
        page for more examples.

    :param bins: Number of snapshots (*slices*) to return.
        If unset, corresponds to the number of unique attribute values defined by ``attr``.
        Required only if ``attr`` is unset, otherwise optional.
    :param attr: Node- or edge-level attribute to
        consider as temporal data. If unset, the method will consider the order of appearance of
        edges or nodes (``rank_first=True``).
    :param str level: Whether to consider node- or edge-level data for slicing. Required if ``attr``
        is a string. Defaults to ``'edge'`` if unset. Choices:

        - ``'edge'``: Edge-level temporal slice. This is the default.

        - ``'node'``: Node-level temporal slice. Alias for ``'source'``.

        - ``'source'``: Node-level slice with temporality defined by the source node
          (pairwise interaction time defined by the source node ``attr``).

        - ``'target'``: Node-level slice with temporality defined by the target node
          (pairwise interaction time defined by the target node ``attr``).

    :param axis: Whether bins should be created by time intervals (``0``) or by number of
        nodes/edges (``1``). Default is ``0``.
    :param qcut: If ``True``, applies `quantile-based discretization
        <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.qcut.html>`__
        for snapshots. Only has an effect if ``attr`` is set. Default is ``False``.
    :param str duplicates: Control whether slices containing duplicates raise an error.
        Accepts ``'drop'`` or ``'raise'``. Default is ``'raise'``.
    :param rank_first: If ``True``, applies `rank-based sort
        <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.rank.html>`__
        by order of appearance of edges, nodes, or an attribute. Automatically set as
        ``True`` if both ``attr`` and ``rank_first`` are unset, otherwise ``False``.
    :param sort: If ``True``, sort unique temporal values after slicing.
        Only applies to categorical temporal data. Default is ``True``.
    :param as_view: If ``False``, returns copies instead of `views
        <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
        of the original graph. Default is ``True``.
    :param fillna: Value to fill null values in attribute data.
    :param Callable apply_func: Function to apply to temporal attribute values.
    """
    if attr is None and bins is None:
        raise ValueError("Either `attr` or `bins` must be set.")
    if axis not in (0, 1):
        raise ValueError("Argument `axis` must be either 0 (time bins) or 1 (node/edge bins).")
    if type(bins) == int and bins < 1:
        raise ValueError("Argument `bins` must be a positive integer if set.")

    # Automatically set `level` if `attr` is not a string.
    if attr is not None and type(attr) != str:
        order, size = self.temporal_order(), self.total_size()
        if not hasattr(attr, "__len__"):
            raise ValueError(
                f"Attribute data must be a sequence of elements, received: {type(attr)}."
            )
        if level is None and order == size:
            raise ValueError(
                "Argument `level` must be set when len(attr) == len(nodes) == len(edges)."
            )
        level = level or ("node" if len(attr) == order else "edge")

    # Set `rank_first` automatically if attribute and bins are unset.
    if attr is None and rank_first is None:
        rank_first = True

    # Obtain static graph object and edge data.
    G = self.to_static()
    edges = pd.DataFrame(G.edges(keys=True) if G.is_multigraph() else G.edges())

    # Set `level` and `edge_column` based on `level` parameter.
    if level in ("node", "source"):
        level, edge_column = "node", 0
    elif level == "target":
        level, edge_column = "node", 1
    elif level is None and len(edges) == 0:
        level = "node"
    else:
        level = "edge"

    # Obtain edge- or node-level attribute data.
    if attr is None:
        times = pd.Series(
            range(G.size() if level == "edge" else G.order()),
            index=G.nodes() if level == "node" else None
        )
    elif type(attr) == dict:
        times = pd.Series(attr)
    elif type(attr) == str:
        times = pd.Series(
            [_[-1] for _ in getattr(G, f"{level}s")(data=attr)],
            index=G.nodes() if level == "node" else None
        )
    elif type(attr) == pd.DataFrame:
        if attr.shape[1] != 1:
            raise ValueError(
                f"Data frame for attribute must have a single column, received: {attr.shape[1]}."
            )
        times = attr.squeeze()
    else:
        times = pd.Series(attr, index=G.nodes() if level == "node" else None)

    # Check if temporal data matches graph order or size.
    if level == "node" and len(times) != G.order():
        raise ValueError(
            f"Length of `attr` ({len(times)}) differs from number of edges ({G.size()})."
        )
    if level == "edge" and len(times) != G.size():
        raise ValueError(
            f"Length of `attr` ({len(times)}) differs from number of nodes ({G.order()})."
        )

    # Fill null values in attribute data.
    if times.isna().any():
        if times.isna().all():
            raise ValueError(
                f"Attribute does not exist at {level} level or contains null values only."
            )
        if fillna is None:
            raise ValueError(
                f"Found null value(s) in attribute data, but `fillna` has not been set."
            )
        times.fillna(fillna, inplace=True)

    # Apply function to time attribute values.
    if apply_func is not None:
        times = times.apply(apply_func)

    # Obtain initial edge temporal values from node-level data.
    if level == "node" and len(edges) > 0:
        times = edges[edge_column].apply(times.get)
        # Obtain node-level (source or target) cut to consider for time bins.
        if axis == 0:
            times = [
                pd.Series(
                    times.loc[nodes.index].values,
                    index=nodes.values
                )
                for nodes in (
                    [edges[edge_column].drop_duplicates().sort_values()]
                )
            ][0]

    # Treat data points sequentially by rank of first appearance.
    if rank_first:
        times = times.rank(method="first")

    if axis == 0:
        if "__len__" in dir(bins):
            # Create intervals closed on left to follow Python's 0-indexing.
            bins = pd.IntervalIndex.from_tuples(bins, closed="left")
        else:
            if bins is not None:
                bins = min(bins or 1, len(times.unique()))
            if bins == 0:
                raise ValueError(f"At least one {level} element is required to slice the graph.")

    # Factorize to ensure strings can be binned,
    # e.g., sortable dates in 'YYYY-MM-DD' format.
    cats = None
    if bins is None or times.dtype.__str__() == "object":
        factorize, cats = pd.factorize(times, sort=sort)
        times = pd.Series(factorize, index=times.index)

    # Slice by number of nodes or edges in each snapshot.
    if axis == 1:
        if qcut:
            raise NotImplementedError("Quantile-based cut (`qcut=True`) not supported for axis=1.")
        if "__len__" in dir(bins):
            raise NotImplementedError("Interval-based `bins` not supported for axis=1.")
        if level == "edge":
            times = pd.Series(
                [i // bins for i in range(len(times))],
                index=times.sort_values().index if sort else times.index
            )
        else:
            index, nodemap = 0, set()
            for i, edge in enumerate(G.edges()):
                nodemap.add(edge[0])
                nodemap.add(edge[1])
                times.iloc[i] = index
                if len(nodemap) >= bins:
                    nodemap = set()
                    index += 1
            if len(nodemap) > 0:
                times.iloc[bins*index:(bins*index)+i] = index
                nodemap = set()
        bins = len(times.unique())

    # Bin data points into time intervals.
    times = getattr(pd, "qcut" if qcut else "cut")(
        times,
        bins if bins is not None else len(times.unique()),
        duplicates=duplicates,
    )\
    .dropna()\
    .cat\
    .remove_unused_categories()

    # Convert categories to string intervals, if applicable.
    if cats is None or bins is not None:
        cats = [f"{'[' if c.closed_left else '('}"
                f"{int(c.left) if cats is None else cats[int(c.left)]}, "
                f"{int(c.right) if cats is None else cats[int(c.right)]}"
                f"{']' if c.closed_right else ')'}"
                for c in times.cat.categories]

    # Check for duplicate categories due to rounded values.
    if len(cats) != len(set(cats)):
        cats = [f"{'[' if c.closed_left else '('}"
                f"{c.left}, {c.right}"
                f"{']' if c.closed_right else ')'}"
                for c in times.cat.categories]

    # Obtain final edge temporal values from node-level data.
    if level == "node" and len(edges) > 0 and axis == 0:
        times = edges[edge_column].apply(times.get)

    # Create temporal graph snapshots.
    indices = (edges if len(edges) > 0 else times
               ).groupby(times, observed=False).groups.values()

    graphs = [
        G.edge_subgraph(
            edges
            .iloc[index]
            .apply(lambda e: (e[0], e[1], e[2]) if self.is_multigraph() else (e[0], e[1]), axis=1)
        )
        if len(edges) > 0
        else G.subgraph(index)
        for index in indices
    ]

    # Create copies instead of views.
    if not as_view:
        graphs = [G.copy() for G in graphs]

    # Create new temporal graph object.
    TG = self.__class__(t=0)
    TG.add_snapshots_from(graphs)
    TG.name = self.name
    if names and cats is not None:
        TG.names = [str(c) for c in cats]
    return TG
