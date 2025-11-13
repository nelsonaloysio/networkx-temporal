from typing import Optional, Union

import networkx as nx
import numpy as np

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_numpy(G: Union[StaticGraph, TemporalGraph], supra: bool = False, **kwargs) -> np.ndarray:
    """ Convert from NetworkX to a dense NumPy adjacency matrix.

    If a single static graph is provided, returns a 2D NumPy array representing the adjacency
    matrix of the graph. If a temporal graph or a list of static graphs is provided, returns a
    3D NumPy array where each slice along the first dimension corresponds to the adjacency
    matrix of a snapshot.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param supra: If ``True`` and a temporal graph is provided, returns the supra-adjacency
        matrix of the temporal graph instead of a stack of adjacency matrices for each snapshot.
        Default: ``False``.
    :param kwargs: Additional keyword arguments passed to
        :func:`networkx.to_numpy_array()`.
    """
    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(G):
        return np.array([to_numpy(H, **kwargs) for H in G])

    return nx.to_numpy_array(G, **kwargs)
