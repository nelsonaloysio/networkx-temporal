from turtle import pd
from typing import List, Optional, Union

import networkx as nx
import pandas as pd

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_pandas(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    source: str = "source",
    target: str = "target",
    nodelist: Optional[list] = None,
    dtype: Optional[object] = None,
    edge_key: Optional[str] = None,
) -> pd.DataFrame:
    """ Convert from NetworkX to `Pandas <https://pandas.org>`__ edge list.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param source: Column name for the source nodes (default: ``'source'``).
    :param target: Column name for the target nodes (default: ``'target'``).
    :param nodelist: List of nodes to consider for conversion. If unset, all nodes are considered.
    :param dtype: Data type of the resulting adjacency matrix. If ``None``, the type is inferred.
    :param edge_key: Column name for the edge keys (default: ``'key'``). Only used for multigraphs.

    :note: Wrapper for `to_pandas_edgelist <https://networkx.org/documentation/stable/reference/generated/networkx.convert_matrix.to_pandas_edgelist.html>`__.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    kwargs = {
        "source": source,
        "target": target,
        "nodelist": nodelist,
        "dtype": dtype,
        "edge_key": edge_key,
    }

    if is_static_graph(graph):
        return nx.to_pandas_edgelist(graph, **kwargs)

    return pd.concat([
        nx.to_pandas_edgelist(g, **kwargs) for g in graph
    ]).reset_index(drop=True)


def from_pandas(
    edgelist: Union[pd.DataFrame, List[pd.DataFrame]],
    source: str = "source",
    target: str = "target",
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    create_using: Optional[Union[StaticGraph, TemporalGraph]] = None,
    edge_attr: Optional[Union[str, List[str], bool]] = True,
    edge_key: Optional[str] = None,
) -> Union[TemporalGraph, StaticGraph]:
    """ Convert from `Pandas <https://pandas.org>`__ edge list to NetworkX.

    :param edgelist: A pandas DataFrame or list of DataFrames representing graph edges.
    :param source: Column name for the source nodes. Default is ``'source'``.
    :param target: Column name for the target nodes. Default is ``'target'``.
    :param directed: If ``True``, returns a directed graph. Default is ``False``.
    :param multigraph: If ``True``, returns a multigraph. Default is ``True``.
    :param edge_attr: Edge attribute key or boolean to load into graph. Default is ``True``.
    :param edge_key: Edge key attribute name for multigraphs. Default is ``None``.
    """
    if not (directed is None or type(directed) == bool):
        raise TypeError(f"Argument `directed` expects a boolean, received: {type(directed)}.")
    if not (multigraph is None or type(multigraph) == bool):
        raise TypeError(f"Argument `multigraph` expects a boolean, received: {type(multigraph)}.")
    if not (create_using is None or is_temporal_graph(create_using) or is_static_graph(create_using)):
        raise TypeError(
            f"Argument `create_using` expects a NetworkX static or temporal graph, "
            f"received: {type(create_using)}."
        )
    if not (create_using is None or (directed is None and multigraph is None)):
        raise ValueError("Arguments `directed` and `multigraph` are exclusive with `create_using`.")

    if type(create_using) is type:
        create_using = create_using()
    if create_using is not None:
        directed = create_using.is_directed()
        multigraph = create_using.is_multigraph()
    if multigraph is None:
        multigraph = True

    create_using = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")

    G = nx.from_pandas_edgelist(
        edgelist,
        source=source,
        target=target,
        create_using=create_using,
        edge_attr=edge_attr,
        edge_key=edge_key,
    )

    if is_static_graph(create_using):
        return G

    from ...transform import from_static
    return from_static(G)
