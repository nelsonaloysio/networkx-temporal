"""
Utility functions for NetworkX static and temporal graphs.

.. rubric:: Summary  - Graph functions

.. autosummary::

    combine_snapshots
    map_to_offsets
    propagate_snapshots
    temporal_edge_similarity
    temporal_node_similarity
    to_adjacency_matrix
    to_supra_adjacency_matrix

.. rubric:: Summary - Node functions

.. autosummary::

    get_node_attributes
    get_unique_node_attributes
    map_attr_to_nodes
    map_edge_attr_to_nodes
    map_partitions_to_nodes
    partition_nodes

.. rubric:: Summary - Edge functions

.. autosummary::

    get_edge_attributes
    get_unique_edge_attributes
    map_attr_to_edges
    map_node_attr_to_edges
    map_partitions_to_edges
    partition_edges

.. rubric:: Summary - Conversion functions

.. autosummary::

    convert.convert
    from_numpy
    from_pandas
    from_scipy
    to_cugraph
    to_cupy
    to_dgl
    to_dynetx
    to_graph_tool
    to_igraph
    to_networkit
    to_numpy
    to_pandas
    to_scipy
    to_snap
    to_stellargraph
    to_teneto
    to_torch_geometric

.. rubric:: Note

The :func:`~networkx_temporal.classes.TemporalGraph.convert` wrapper is available as
a top-level function and also as a :class:`~networkx_temporal.classes.TemporalGraph` method:

.. code-block:: python

    >>> import networkx_temporal as tx
    >>> TG = tx.example_sbm_graph()
    >>> TG.convert("igraph")

    [<igraph.Graph at 0x108198950>,
     <igraph.Graph at 0x168589950>,
     <igraph.Graph at 0x168589a50>]

.. code-block:: python

    >>> G = TG.to_static()
    >>> tx.convert(G, "igraph")

    <igraph.Graph at 0x168589150>

.. rubric:: Functions
"""

from .convert.cugraph import to_cugraph
from .convert.cupy import to_cupy
from .convert.dgl import to_dgl
from .convert.dynetx import to_dynetx
from .convert.graph_tool import to_graph_tool
from .convert.igraph import to_igraph
from .convert.networkit import to_networkit
from .convert.numpy import from_numpy, to_numpy
from .convert.pandas import from_pandas, to_pandas
from .convert.scipy import from_scipy, to_scipy
from .convert.snap import to_snap
from .convert.stellargraph import to_stellargraph
from .convert.teneto import to_teneto
from .convert.torch_geometric import to_torch_geometric
from .edges import *
from .graph import *
from .nodes import *

__all__ = (
    "combine_snapshots",
    "map_to_offsets",
    "propagate_snapshots",
    "temporal_edge_similarity",
    "temporal_node_similarity",
    "to_adjacency_matrix",
    "to_supra_adjacency_matrix",
    "get_node_attributes",
    "get_unique_node_attributes",
    "map_attr_to_nodes",
    "map_edge_attr_to_nodes",
    "map_partitions_to_nodes",
    "partition_nodes",
    "get_edge_attributes",
    "get_unique_edge_attributes",
    "map_attr_to_edges",
    "map_node_attr_to_edges",
    "map_partitions_to_edges",
    "partition_edges",
    "from_numpy",
    "from_pandas",
    "from_scipy",
    "to_cugraph",
    "to_cupy",
    "to_dgl",
    "to_dynetx",
    "to_graph_tool",
    "to_igraph",
    "to_networkit",
    "to_numpy",
    "to_pandas",
    "to_scipy",
    "to_snap",
    "to_stellargraph",
    "to_teneto",
    "to_torch_geometric",
)