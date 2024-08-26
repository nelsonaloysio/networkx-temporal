from typing import Optional, Union

import networkx as nx


def TemporalGraph(
    t: Optional[int] = None,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]] = None,
):
    """
    Standard class for handling temporal graphs.

    This class inherits a NetworkX
    `Graph <https://networkx.org/documentation/stable/reference/classes/graph.html>`__,
    `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__,
    `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__, or
    `MultiDiGraph <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__,
    depending on the choice of parameters given. It includes all methods implemented by them, such
    as ``add_node``, ``add_edge``, ``remove_node``, ``remove_edge``, ``subgraph``, ``to_directed``,
    and ``to_undirected``, as well as additional methods for handling temporal graphs and temporal
    snapshots.

    .. rubric:: Example

    The following example demonstrates how to create a temporal graph with two snapshots:

    .. code-block:: python

       >>> import networkx_temporal as tx
       >>>
       >>> TG = tx.TemporalGraph(directed=True, multigraph=False, t=2)
       >>>
       >>> TG[0].add_edge("a", "b")
       >>> TG[1].add_edge("c", "b")
       >>>
       >>> print(TG)

       TemporalDiGraph (t=2) with 4 nodes and 2 edges

    .. hint::

       Setting ``t`` greater than ``1`` will create a list of NetworkX graph objects, each
       representing a snapshot in time. Unless dynamic node attributes are required, it is
       recommended to use the :func:`~networkx_temporal.TemporalGraph.slice` method instead,
       in order to create less resource-demanding graph `views
       <https://networkx.org/documentation/stable/reference/classes/generated/networkx.classes.graphviews.subgraph_view.html>`__
       on the fly.

    .. seealso::

       * The `official NetworkX documentation
         <https://networkx.org/documentation/stable/reference/classes/index.html>`__
         for a list of methods available for each graph type.
       * The `Examples: Basic operations
         <https://networkx-temporal.readthedocs.io/en/latest/examples.html>`__
         page for more examples on building a temporal graph.

    :param int t: Number of temporal graphs to initialize. Optional. Default is ``1``.
    :param directed: If ``True``, returns a
        `DiGraph <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__.
        Defaults to ``False``.
    :param multigraph: If ``True``, returns a
        `MultiGraph <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__.
        Defaults to ``False``.
    :param object create_using: NetworkX graph object to use as template. Optional.
        Does not allow ``directed`` and ``multigraph`` parameters when set.
    """
    assert directed is None or type(directed) == bool,\
        f"Argument `directed` must be a boolean, received: {type(directed)}."
    assert multigraph is None or type(multigraph) == bool,\
        f"Argument `multigraph` must be a boolean, received: {type(multigraph)}."
    assert create_using is None or type(create_using) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph),\
        f"Argument `create_using` must be a NetworkX graph object, received: {type(create_using)}."
    assert create_using is None or (directed is None and multigraph is None),\
        "Arguments `directed` and `multigraph` should be `None` when `create_using` is given."

    if create_using is not None:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()

    from .graph import TemporalGraph, TemporalDiGraph, TemporalMultiGraph, TemporalMultiDiGraph
    return locals()[f"Temporal{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph"](t=t)


def empty_graph(
    t: Optional[int] = None,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]] = None,
) -> TemporalGraph:
    """
    Returns an empty :class:`~networkx_temporal.TemporalGraph` object.

    This function may optionally be used to create a temporal graph with the desired properties.
    """
    return TemporalGraph(t=t, directed=directed, multigraph=multigraph, create_using=create_using)
