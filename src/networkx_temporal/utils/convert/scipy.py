from typing import Any, Optional, Union

import scipy.sparse as sp

try:
    from networkx import from_scipy_sparse_array, to_scipy_sparse_array
except ImportError:
    from networkx import (from_scipy_sparse_matrix as from_scipy_sparse_array,
                            to_scipy_sparse_matrix as to_scipy_sparse_array)
try:
    from scipy.sparse import csr_array
except ImportError:
    from scipy.sparse import csr_matrix as csr_array

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_scipy(
    G: Union[StaticGraph, TemporalGraph],
    supra: bool = False,
    nodelist: list = None,
    dtype: Any = None,
    weight: Optional[str] = "weight",
    format: str = "csr",
) -> csr_array:
    """ Convert from NetworkX to a sparse SciPy adjacency matrix.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param supra: If ``True`` and a temporal graph is provided, returns the supra-adjacency
        matrix of the temporal graph instead of a stack of adjacency matrices for each snapshot.
        Default: ``False``.
    :param nodelist: List of nodes specifying the order of the rows and columns
        in the resulting adjacency matrix. If ``None``, the order is
        ``list(G.nodes())``.
    :param dtype: Data type of the resulting adjacency matrix. If ``None``, the type is inferred.
    :param weight: The edge attribute key used to compute edge weights (default: ``'weight'``).
        If ``None``, all edge weights are considered as ``1``.
    :param format: The sparse matrix format of the resulting adjacency matrix.
        Accepts ``'csr'`` (compressed sparse row), ``'csc'`` (compressed sparse column),
        ``'dok'`` (dictionary of keys), or ``'lil'`` (list of lists). Default is ``'csr'``.
    """
    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")
    if supra and not is_temporal_graph(G):
        raise ValueError("The 'supra' parameter is only valid for temporal graphs.")

    kwargs = {"nodelist": nodelist, "dtype": dtype, "weight": weight, "format": format}

    if is_temporal_graph(G):
        if supra:
            order = sum(snapshot.order() for snapshot in G.snapshots())
            supra_adj = sp.dok_matrix((order, order), dtype=kwargs.get("dtype", float))
            offset = 0
            for snapshot in G.snapshots():
                n = snapshot.order()
                noffset = offset + n
                supra_adj[offset:noffset, offset:noffset] = to_scipy_sparse_array(snapshot,
                                                                                  **kwargs)
                offset = noffset
            return csr_array(supra_adj)
        return [to_scipy_sparse_array(snapshot, **kwargs) for snapshot in G.snapshots()]

    return to_scipy_sparse_array(G, **kwargs)
