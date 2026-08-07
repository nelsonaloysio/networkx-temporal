from typing import List, Optional, Union

import networkx as nx
import numpy as np

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph

try:
    from networkx import from_numpy_array, to_numpy_array
except ImportError:  # networkx <= 2.6 (#4238)
    from networkx import (from_numpy_matrix as from_numpy_array,
                          to_numpy_matrix as to_numpy_array)


def to_numpy(
    graph: Union[TemporalGraph, StaticGraph, List[StaticGraph]],
    supra: Optional[bool] = False,
    weight: Optional[str] = "weight",
    interslice_weight: Optional[float] = 1.0,
    nodelist: Optional[list] = None,
    dtype: Optional[object] = None,
    **kwargs,
) -> Union[np.ndarray, List[np.ndarray]]:
    """ Convert from NetworkX to dense `NumPy <https://numpy.org>`__ array.

    :param object graph: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`,
        a single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param supra: If ``True`` and a temporal graph is provided, returns the supra-adjacency
        matrix of the temporal graph instead of a list of adjacency matrices, one per snapshot.
        Default: ``False``.
    :param weight: Edge attribute key used to compute edge weights (default: ``'weight'``). If
        ``None``, all edge weights are considered as ``1``.
    :param interslice_weight: Weight of inter-snapshot edges in the supra-adjacency matrix.
        Only used if ``supra=True``.
    :param dtype: Data type of the intermediate adjacency matrix. Defaults to ``float32``.
    """
    if not (is_temporal_graph(graph) or is_static_graph(graph)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    kwargs.update({"weight": weight, "nodelist": nodelist, "dtype": dtype})

    if is_static_graph(graph):
        return to_numpy_array(graph, **kwargs)

    if supra:
        from ..graph import to_supra_adjacency_matrix
        return np.array(
            to_supra_adjacency_matrix(
                graph, interslice_weight=interslice_weight, device="cpu", **kwargs
            )
            .todense()
        )
    return [to_numpy(g, **kwargs) for g in graph]



def from_numpy(
    adj: Union[np.ndarray, List[np.ndarray]],
    directed: Optional[bool] = False,
    multigraph: Optional[bool] = True,
    edge_attribute: Optional[str] = "weight",
) -> Union[TemporalGraph, StaticGraph]:
    """ Convert from dense `NumPy <https://numpy.org>`__ array to NetworkX.

    :param adj: A NumPy array or list of arrays representing graph adjacencies.
    :param directed: If ``True``, creates a directed graph. Default is ``False``.
    :param multigraph: If ``True``, creates a multigraph. Default is ``True``.
    :param edge_attribute: Edge attribute key used to store edge weights. Default is ``'weight'``.
    """
    multigraph = True if multigraph is None else multigraph
    create_using = getattr(nx, f"{'Multi' if multigraph else ''}{'Di' if directed else ''}Graph")

    if isinstance(adj, np.ndarray):
        return from_numpy_array(
            adj,
            parallel_edges=multigraph,
            create_using=create_using,
            edge_attr=edge_attribute,
        )

    from ...transform import from_snapshots
    return from_snapshots([
        from_numpy_array(
            array,
            parallel_edges=multigraph,
            create_using=create_using,
            edge_attr=edge_attribute
        )
        for array in adj
    ])
