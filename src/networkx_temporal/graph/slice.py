from __future__ import annotations

from typing import Any, Callable, Optional, Union

import pandas as pd

from ..transform import from_snapshots
from ..typing import TemporalGraph, Literal


def slice(
    self,
    bins: Optional[int] = None,
    attr: Optional[Union[str, list, dict, pd.DataFrame, pd.Series]] = None,
    level: Optional[Literal["edge", "node", "source", "target"]] = None,
    qcut: bool = False,
    duplicates: Literal["raise", "drop"] = "raise",
    rank_first: Optional[bool] = None,
    sort: bool = True,
    as_view: bool = True,
    fillna: Optional[Any] = None,
    apply_func: Optional[Callable[..., Any]] = None,
) -> TemporalGraph:
    """
    Slices temporal graph into snapshots, returning a new temporal graph object.

    No data is lost when using this method, as it includes all nodes and edges from the original
    graph. Note that the returned object may return duplicate nodes, if they are connected to
    other nodes in multiple snapshots; and edges, if ``duplicates`` is not set to ``'raise'``.

    .. rubric:: Example

    Slicing a temporal graph into two snapshots based on the edge-level ``time`` attribute:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalDiGraph()
       >>> # TG = tx.temporal_graph(directed=True, multigraph=False)
       >>>
       >>> TG.add_edge("a", "b", time=0)
       >>> TG.add_edge("c", "b", time=1)
       >>>
       >>> TG = TG.slice(attr="time")
       >>>
       >>> print(TG)

       TemporalDiGraph (t=2) with 4 nodes and 2 edges

    Calling this method again on the same object, now with ``bins=1``, will :func:`~networkx_temporal.TemporalGraph.flatten` the graph:

    .. code-block:: python

       >>> TG = TG.slice(bins=1)
       >>>
       >>> print(TG)

       TemporalMultiDiGraph (t=1) with 3 nodes and 2 edges

    .. hint::

        By default, `views <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
        of the original graph are returned to avoid memory overhead. If the resulting
        snapshots need to be modified, set ``as_view=False`` to return copies instead.

    .. seealso::

        The
        `Examples: Slice temporal graph
        <https://networkx-temporal.readthedocs.io/en/latest/examples/basics.html#slice-temporal-graph>`__
        page for more examples using this function.

    :param bins: Number of snapshots (*slices*) to return.
        If unset, corresponds to the number of unique attribute values defined by ``attr``.
        Required only if ``attr`` is unset, otherwise optional.
    :param attr: Node- or edge-level attribute to
        consider as temporal data. If unset, the method will consider the order of appearance of
        edges or nodes (``rank_first=True``).
    :param str level: Whether to consider node- or edge-level data for slicing. Required if ``attr``
        is a string. Defaults to ``'edge'`` if unset. Choices:

        - ``'edge'``: Edge-level temporal slice.

        - ``'node'``: Node-level temporal slice. Alias for ``'source'``.

        - ``'source'``: Node-level slice with temporality defined by the source node
          (interaction times are considered as that of the source node).

        - ``'target'``: Node-level slice with temporality defined by the target node
          (interaction times are considered as that of the target node).

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
    :param apply_func: Function to apply to temporal attribute values.

    :rtype: TemporalGraph
    """
    assert self.data,\
        "Temporal graph is empty."
    assert sum(self.order()),\
        "Temporal graph has no nodes."
    assert sum(self.size()),\
        "Temporal graph has no edges."
    assert attr is not None or bins is not None,\
        "Argument `bins` must be set if `attr` is unset."
    assert bins is None or (type(bins) == int and bins > 0),\
        "Argument `bins` must be a positive integer if set."

    # Automatically set `level` if `attr` is not a string.
    if attr is not None and type(attr) != str:
        order, size = self.temporal_order(), self.temporal_size()

        assert hasattr(attr, "__len__"),\
            f"Attribute data must be a list, dictionary or sequence of elements, received: {type(attr)}."
        assert level is not None or order != size,\
            "Parameter `level` must be set for graphs with the same number of nodes and edges."

        level = level or ("node" if len(attr) == order else "edge")

    # Set `rank_first` automatically if attribute data is unset.
    if attr is None and rank_first is None:
        rank_first = True

    # Set `level` and `node_column` based on `level` parameter.
    if level in ("node", "source"):
        level, node_column = "node", 0
    elif level == "target":
        level, node_column = "node", 1
    else:
        level = "edge"

    # Obtain static graph object and edge data.
    G = self.to_static()
    edges = pd.DataFrame(G.edges(keys=True) if G.is_multigraph() else G.edges())

    # Obtain edge- or node-level attribute data.
    if attr is None:
        times = pd.Series(
            range(G.size() if level == "edge" else G.order()),
            index=G.nodes() if level == "node" else None
        )

    elif type(attr) == str:
        times = pd.Series(
            [_[-1] for _ in getattr(G, f"{level}s")(data=attr)],
            index=G.nodes() if level == "node" else None
        )

    elif type(attr) == dict:
        times = pd.Series(attr)

    elif type(attr) == pd.DataFrame:
        assert attr.shape[1] == 1,\
            f"Data frame for attribute data must have a single column, received: {attr.shape[1]}."
        times = attr.squeeze()

    else:
        times = pd.Series(attr, index=G.nodes() if level == "node" else None)

    # Check if temporal data matches graph order or size.
    assert level == "node" or len(times) == G.size(),\
        f"Length of `attr` ({len(times)}) differs from number of edges ({G.size()})."
    assert level == "edge" or len(times) == G.order(),\
        f"Length of `attr` ({len(times)}) differs from number of nodes ({G.order()})."

    # Fill null values in attribute data.
    if times.isna().any():
        assert not times.isna().all(),\
            f"Attribute does not exist at {level} level or contains null values only."
        assert fillna is not None,\
            f"Found null value(s) in attribute data, but `fillna` has not been set."
        times.fillna(fillna, inplace=True)

    # Apply function to time attribute values.
    if apply_func is not None:
        times = times.apply(apply_func)

    # Obtain initial edge temporal values from node-level data.
    if level == "node":
        times = edges[node_column].apply(times.get)

        # Obtain node-level (source or target) cut to consider for time bins.
        times = [
            pd.Series(
                times.loc[nodes.index].values,
                index=nodes.values
            )
            for nodes in (
                [edges[node_column].drop_duplicates().sort_values()]
            )
        ][0]

    # Treat data points sequentially.
    if rank_first:
        times = times.rank(method="first")

    # Limit number of bins to total unique time values.
    if bins is not None:
        bins = min(bins or 0, len(times.unique()))

    # Factorize to ensure strings can be binned,
    # e.g., sortable dates in 'YYYY-MM-DD' format.
    cats = None
    if times.dtype.__str__() == "object":
        factorize, cats = pd.factorize(times, sort=sort)
        times = pd.Series(factorize, index=times.index)

    # Bin data points into time intervals.
    times = getattr(pd, "qcut" if qcut else "cut")(
        times,
        bins or len(times.unique()),
        duplicates=duplicates,
    )\
    .cat\
    .remove_unused_categories()

    # Convert categories to string intervals, if applicable.
    if bins is not None or cats is None:
        cats = [f"{'[' if c.closed_left else '('}"
                f"{int(c.left) if cats is None else cats[int(c.left)]}, "
                f"{int(c.right) if cats is None else cats[int(c.right)]}"
                f"{']' if c.closed_right else ')'}"
                for c in times.cat.categories]

    # Obtain final edge temporal values from node-level data.
    if level == "node":
        times = edges[node_column].apply(times.get)

    # Create temporal graph snapshots.
    graphs = [
        G.edge_subgraph(
            edges
            .iloc[index]
            .apply(lambda e: (e[0], e[1], e[2]) if self.is_multigraph() else (e[0], e[1]), axis=1)
        )
        for index in edges.groupby(times, observed=False).groups.values()
    ]

    # Create copies instead of views.
    if not as_view:
        graphs = [G.copy() for G in graphs]

    # Create new temporal graph object.
    TG = from_snapshots(graphs)
    TG.name = self.name
    TG.names = list(cats)

    return TG
