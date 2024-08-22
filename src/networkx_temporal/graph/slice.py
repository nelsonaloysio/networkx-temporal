from __future__ import annotations

from typing import Any, Callable, Optional, Union

import pandas as pd

from ..transform import from_snapshots
from ..typing import TemporalGraph, Literal


def slice(
    self,
    bins: Optional[int] = None,
    attr: Optional[Union[str, list, dict, pd.DataFrame, pd.Series]] = None,
    attr_level: Optional[Literal["node", "edge"]] = None,
    node_level: Optional[Literal["source", "target"]] = None,
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
       >>> TG = tx.TemporalGraph(directed=True, multigraph=True)
       >>>
       >>> TG.add_edge("a", "b", time=0)
       >>> TG.add_edge("c", "b", time=1)
       >>>
       >>> TG = TG.slice(attr="time")
       >>>
       >>> print(TG)

       TemporalMultiDiGraph (t=2) with 4 nodes and 2 edges

    Calling this method again on the same object, now with ``bins=1``, will :func:`~networkx_temporal.TemporalGraph.flatten` the graph:

    .. code-block:: python

       >>> TG = TG.slice(bins=1)
       >>>
       >>> print(TG)

       TemporalMultiDiGraph with 3 nodes and 2 edges

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
    :param str attr_level: Level of temporal attribute, either ``'node'`` or ``'edge'``.
        Required if ``attr`` is a string. Defaults to ``'edge'`` if unset.
    :param str node_level: Level of temporal nodes to consider, either ``'source'`` or ``'target'``.
        Defaults to ``'source'`` if unset. Only has an effect for node-level attribute data.
    :param qcut: If ``True``, applies `quantile-based discretization
        <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.qcut.html>`__
        for snapshots. Only has an effect if ``attr`` is set. Default is ``False``.
    :param str duplicates: Control whether slices containing duplicates raise an error.
        Accepts ``'drop'`` or ``'raise'``. Default is ``'raise'``.
    :param rank_first: If ``True``, applies `rank-based sort
        <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.rank.html>`__
        by order order of appearance of edges or nodes. Automatically set as
        ``True`` if both ``attr`` and ``rank_first`` are unset, otherwise ``False``.
    :param sort: If ``True``, sort unique temporal values after slicing.
        Only applies to categorical temporal data. Default is ``True``.
    :param as_view: If ``False``, returns copies instead of `views
        <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
        of the original graph. Default is ``True``.
    :param fillna: Value to fill null values in attribute data.
    :param apply_func: Function to apply to temporal attribute values.
    """
    assert self.data, "Temporal graph is empty."
    assert sum(self.order()), "Temporal graph has no nodes."
    assert sum(self.size()), "Temporal graph has no edges."

    # Set default slicing method (by order of appearance of edges).
    if attr is None:
        attr_level = "edge" if attr_level is None else attr_level
        rank_first = True if rank_first is None else rank_first

    # Automatically set `attr_level` if attribute data is not a string.
    elif type(attr) != str:
        length = getattr(attr, "__len__", lambda: None)()

        assert length is not None,\
            f"Attribute data must be a list, dictionary or sequence of elements, received: {type(attr)}."

        assert attr_level is not None or not length == self.temporal_order() == self.temporal_size(),\
            "Attribute level must be set for graphs with the same number of nodes and edges."

        attr_level = "node" if length == self.temporal_order() else "edge"

    # Set default attribute level (edge or source if node-level).
    if attr is not None and attr_level is None:
        attr_level = "edge"

    elif attr_level == "node" and node_level is None:
        node_level = "source"

    # Check if arguments are valid.
    assert attr is not None or bins is not None,\
        "Argument `bins` must be set if `attr` is unset."

    assert bins is None or (type(bins) == int and bins > 0),\
        "Argument `bins` must be positive integer if set."

    assert type(attr) != str or attr_level in ("node", "edge"),\
        "Argument `attr_level` must be either 'node' or 'edge' when `attr` is a string."

    assert node_level is None or attr_level == "node",\
        "Argument `node_level` is not applicable to edge-level attribute data."

    assert node_level in ("source", "target") or attr_level != "node",\
        "Argument `node_level` must be either 'source' or 'target' when slicing node-level attribute data."

    # Obtain static graph object and edge data.
    G = self.to_static()
    edges = pd.DataFrame(G.edges(keys=True) if G.is_multigraph() else G.edges())

    # Obtain node- or edge-level attribute data.
    if attr is None:
        times = pd.Series(
            range(G.size() if attr_level == "edge" else G.order()),
            index=G.nodes() if attr_level == "node" else None
        )

    elif type(attr) == str:
        times = pd.Series(
            [_[-1] for _ in getattr(G, f"{attr_level}s")(data=attr)],
            index=G.nodes() if attr_level == "node" else None
        )

    elif type(attr) == dict:
        times = pd.Series(attr)

    elif type(attr) == pd.DataFrame:
        times = attr.squeeze()

    else:
        times = pd.Series(attr, index=G.nodes() if attr_level == "node" else None)

    # Check if attribute data has the right length.
    assert attr_level == "node" or len(times) == G.size(),\
        f"Length of `attr` ({len(times)}) differs from number of edges ({G.size()})."

    assert attr_level == "edge" or len(times) == G.order(),\
        f"Length of `attr` ({len(times)}) differs from number of nodes ({G.order()})."

    # Fill null values in attribute data.
    if times.isna().any():
        assert not times.isna().all(),\
            f"Attribute does not exist at {attr_level} level or contains null values only."

        assert fillna is not None,\
            f"Found null value(s) in attribute data, but `fillna` has not been set."

        times.fillna(fillna, inplace=True)

    # Apply function to time attribute values.
    if apply_func is not None:
        times = times.apply(apply_func)

    # Select node-level column by position.
    if attr_level == "node":
        if node_level in (None, "source"):
            node_level = 0
        elif node_level == "target":
            node_level = 1

    # Obtain edge temporal values from node-level data [0/1].
    if attr_level == "node":
        times = edges[node_level].apply(times.get)

    # Obtain node-wise (source or target) cut to consider for time bins.
    if node_level:
        times = [
            pd.Series(
                times.loc[nodes.index].values,
                index=nodes.values
            )
            for nodes in (
                [edges[node_level].drop_duplicates().sort_values()]
            )
        ][0]

    # Treat data points sequentially.
    if rank_first:
        times = times.rank(method="first")

    # Consider unique time values from attribute data.
    if not bins:
        bins = len(times.unique())

    # Slice data in a given nuber of time steps.
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
        bins,
        duplicates=duplicates,
    )\
    .cat\
    .remove_unused_categories()

    # Convert categories to string intervals.
    cats = [f"{'[' if c.closed_left else '('}"
            f"{int(c.left) if cats is None else cats[int(c.left)]}, "
            f"{int(c.right) if cats is None else cats[int(c.right)]}"
            f"{']' if c.closed_right else ')'}"
            for c in times.cat.categories]

    # Obtain edge temporal values from node-level data.
    if node_level:
        times = edges[node_level].apply(times.get)

    # Group edge indices by time.
    indices = edges.groupby(times, observed=False).groups

    # Create temporal graph snapshots.
    graphs = [
        G.edge_subgraph(
            edges
            .iloc[index]
            .apply(lambda e: (e[0], e[1], e[2]) if self.is_multigraph() else (e[0], e[1]), axis=1)
        )
        for index in indices.values()
    ]

    # Create copies instead of views.
    if not as_view:
        graphs = [G.copy() for G in graphs]

    # Create new temporal graph object.
    TG = from_snapshots(graphs)
    TG.name = self.name
    TG.names = cats
    return TG
