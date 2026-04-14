from typing import List, Optional

import networkx as nx
from networkx import NetworkXError

from ..classes.types import is_temporal_graph
from ..typing import TemporalGraph, Literal


def combine_snapshots(graphs: List[TemporalGraph]) -> TemporalGraph:
    """ Returns temporal graph with combined snapshots.

    Each snapshot in the resulting temporal graph is the union of the corresponding
    snapshots at each index :math:`t` from ``graphs``. All input temporal graphs
    must have the same number of snapshots.

    .. seealso::

        The `Examples → Basic operations → Combine snapshots
        <../examples/basics.html#propagate-snapshots>`__  page for an example.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG1 = tx.temporal_graph()
        >>> TG2 = tx.temporal_graph()
        >>>
        >>> TG1.add_edge("a", "b")
        >>> TG2.add_edge("c", "b")
        >>>
        >>> TG = tx.combine_snapshots([TG1, TG2])
        >>> print(TG)

        TemporalGraph with 1 snapshots and 3 nodes and 2 edges

    :param object graphs: A list of :class:`~networkx_temporal.classes.TemporalGraph`
        objects.
    """
    if type(graphs) != list:
        raise TypeError(f"Argument `graphs` must be a list, received: {type(graphs)}.")
    if len(graphs) == 0:
        raise ValueError("Argument `graphs` must contain at least one graph.")

    temporal = all(is_temporal_graph(G) for G in graphs)
    if not temporal:
        raise NetworkXError("All inputs must be temporal NetworkX graphs.")

    multigraph = all(G.is_multigraph() == graphs[0].is_multigraph() for G in graphs)
    if not multigraph:
        raise NetworkXError("All inputs must be either multigraph or non-multigraph objects.")

    if any(len(G) != len(graphs[0]) for G in graphs):
        raise ValueError("All temporal graphs must have the same number of snapshots.")

    # Initialize empty temporal graph of the same type.
    TG = graphs[0].__class__(t=0)

    TG.add_snapshots_from([
        nx.compose_all([TG[t] for TG in graphs])
        for t in range(len(graphs[0]))
    ])

    return TG


def propagate_snapshots(
    TG: TemporalGraph,
    method: Literal["ffill", "bfill"] = "ffill",
    delta: Optional[int] = None,
) -> TemporalGraph:
    """ Propagates nodes and edges across snapshots.

    Returns a temporal graph where nodes and edges are preserved
    among snapshots.

    .. seealso::

        The `Examples → Basic operations → Propagate snapshots
        <../examples/basics.html#propagate-snapshots>`__  page for an example.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: The propagation method. Can be either:

       - ``'ffill'``: propagates nodes and edges forward in time
         (from earlier to later snapshots);

       - ``'bfill'``: propagates nodes and edges backward in time
         (from later to earlier snapshots).
    :param delta: The number of snapshots to propagate over.
        If ``None`` (default), propagates over all snapshots.
    """
    if not is_temporal_graph(TG):
        raise TypeError("Argument `TG` must be a temporal NetworkX graph.")
    if method not in ("ffill", "bfill"):
        raise ValueError("Argument `method` must be one of ('ffill', 'bfill').")

    TG = TG.copy()

    if method == "ffill":
        for t in range(1, len(TG)):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(max(0, t - delta if delta is not None else 0), t + 1)
            ])
    else:  # method == "bfill"
        for t in range(len(TG)-2, -1, -1):
            TG.graphs[t] = nx.compose_all([
                TG[t]
                for t in range(t, min(len(TG), t + (delta if delta is not None else len(TG))))
            ])

    return TG


def temporal_edge_matrix(
    TG: TemporalGraph,
    method: Literal["jaccard", "union", "intersect", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns matrix of edge overlap over time.

    .. seealso:: The `Examples → Explore → Temporal edge matrix
        <../examples/basics.html#temporal-edge-matrix>`__  page for an example.

    .. rubric:: Example

    Loading and computing similarity among edge sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> tx.temporal_edge_matrix(TG, method="jaccard")

        [[1.0,  0.05, 0.10],
         [0.11, 1.0,  0.08],
         [0.11, 0.08, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: Measure to consider. Default is ``'jaccard'``. Available choices:

        - ``'jaccard'``: Jaccard similarity (intersection over union);

        - ``'intersect'``: intersection over size of first set;

        - ``'union'``: union over size of first set;

        - ``'geometric'``: geometric mean of set overlaps.

        - ``'dice'``: Dice coefficient (2 * intersection over sum of sizes).
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    data = {edge: i for i, edge in enumerate(TG.edges(copies=False))}
    data = [[data[edge] for edge in edges] for edges in TG.edges()]
    return _temporal_matrix(data, method=method, na_diag=na_diag)


def temporal_node_matrix(
    TG: TemporalGraph,
    method: Literal["jaccard", "union", "intersect", "geometric"] = "jaccard",
    na_diag: bool = False,
) -> List[list]:
    """ Returns matrix of node overlap over time.

    .. rubric:: Example

    Loading and computing similarity among node sets from the
    :func:`~networkx_temporal.generators.example_sbm_graph` dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> tx.temporal_node_matrix(TG, method="jaccard")

        [[1.0,  1.0,  0.99],
         [1.0,  1.0,  0.99],
         [0.99, 0.99, 1.0 ]]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param method: Measure to consider. Default is ``'jaccard'``. Available choices:

        - ``'jaccard'``: Jaccard similarity coefficient;

        - ``'intersect'``: intersection over size of first set;

        - ``'union'``: union over size of first set;

        - ``'geometric'``: geometric mean of set overlaps.

        - ``'dice'``: Dice coefficient (2 * intersection over sum of sizes).
    :param na_diag: If ``True``, sets diagonal values to ``None``.
    """
    return _temporal_matrix(TG.nodes(), method=method, na_diag=na_diag)


def _temporal_matrix(data: list, method: str, na_diag: bool = False) -> List[list]:
    values = []
    for i in range(len(data)):
        values.append([])
        for j in range(len(data)):
            if na_diag and i == j:
                values[i].append(None)
                continue
            data_i = set(data[i])
            data_j = set(data[j])
            intersection = data_i.intersection(data_j)
            union = data_i.union(data_j)
            if method == "jaccard":
                val = (len(intersection) / len(union)
                      ) if len(union) > 0 else 0
            elif method == "union":
                val = (len(union) / len(data_i)
                      ) if len(data_i) > 0 else 0
            elif method == "intersect":
                val = (len(intersection) / len(data_i)
                      ) if len(data_i) > 0 else 0
            elif method == "geometric":
                val = (len(intersection) ** 2 / (len(data_i) * len(data_j))
                      ) if len(data_i) > 0 and len(data_j) > 0 else 0
            elif method == "dice":
                val = (2 * len(intersection) / (len(data_i) + len(data_j))
                      ) if (len(data_i) + len(data_j)) > 0 else 0
            values[i].append(val)
    return values
