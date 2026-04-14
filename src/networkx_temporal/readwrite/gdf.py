from io import BufferedReader, BufferedWriter, BytesIO, StringIO, TextIOWrapper
from typing import Optional, Union

import networkx as nx

TYPES = {
    "VARCHAR": str,
    "INT": int,
    "LONG": int,
    "FLOAT": float,
    "DOUBLE": float,
    "BOOLEAN": bool,
}

QUOTES = {
    "'": "single",
    '"': "double",
}


@staticmethod
def read_gdf(
    file: Union[str, BufferedReader, BytesIO, StringIO, TextIOWrapper],
    directed: Optional[bool] = None,
    multigraph: Optional[bool] = None,
    weighted: Optional[bool] = True,
    node_attr: Optional[Union[list, bool]] = True,
    edge_attr: Optional[Union[list, bool]] = True,
    encoding: str = "utf-8",
    errors: str = "strict",
) -> nx.Graph:
    """
    Returns a NetworkX graph object from GDF file or object.

    .. seealso::

       The `API Reference <https://networkx-gdf.readthedocs.io/en/stable/api.html>`__
       of the ``networkx_gdf`` package for format details.

    :param object file: File object or string containing path to GDF file.
    :param directed: Consider edges as directed or undirected. Optional. Default is ``None``.

        * If ``None``, decides based on ``'directed'`` edge attribute in file, if it exists.
            In case it does not exist, the graph will be considered as undirected.

        * If ``True``, returns a `DiGraph
            <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__
            or `MultiDiGraph
            <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__
            object.

        * If ``False``, returns a `Graph
            <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
            or `MultiGraph
            <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
            object.

    :param multigraph: Consider multiple edges among pairs of nodes. Optional. Default
        is ``None``.

        * If ``None``, decides based on number of edges among node pairs. In case of multiple
            edges among the same node pairs, the graph will be considered as a multigraph,
            preserving dynamic edge-level attributes.

        * If ``True``, returns a `MultiGraph
            <https://networkx.org/documentation/stable/reference/classes/multigraph.html>`__
            or `MultiDiGraph
            <https://networkx.org/documentation/stable/reference/classes/multidigraph.html>`__
            object.

        * If ``False``, **sums edge weights** and returns a `Graph
            <https://networkx.org/documentation/stable/reference/classes/graph.html>`__
            or `DiGraph
            <https://networkx.org/documentation/stable/reference/classes/digraph.html>`__
            object.

    :param weighted: Consider edge weights. Optional. Default is ``True``.
        Only applicable if ``multigraph`` is manually set as ``False``.

    :param node_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

        * If a ``list``, only the specified attributes will be considered.

        * If ``True``, all node attributes will be considered.

        * If ``False``, no node attributes will be considered.

    :param edge_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

        * If a ``list``, only the specified attributes will be considered.

        * If ``True``, all edge attributes will be considered.

        * If ``False``, no edge attributes will be considered.

    :param encoding: The encoding of the file. Default is ``'utf-8'``.
        For a list of possible values, see `Python documentation: Standard Encodings
        <https://docs.python.org/3/library/codecs.html#standard-encodings>`__.
    :param errors: The error handling scheme. Default is ``'strict'``.
        For a list of possible values, see `Python documentation: Error Handlers
        <https://docs.python.org/3/library/codecs.html#error-handlers>`__.

    :note: Wrapper function for
        `networkx_gdf.read_gdf
        <https://networkx-gdf.readthedocs.io/en/stable/api.html#networkx_gdf.read_gdf>`__.
    """
    try:
        from networkx_gdf import read_gdf
    except ImportError as e:
        raise ImportError(
            "The `networkx_gdf` package is required to read GDF files. "
            "Please install it via `pip install networkx_gdf`."
        ) from e

    return read_gdf(
        path=file,
        directed=directed,
        multigraph=multigraph,
        weighted=weighted,
        node_attr=node_attr,
        edge_attr=edge_attr,
        encoding=encoding,
        errors=errors,
    )


def write_gdf(
    G: nx.Graph,
    file: Optional[Union[str, BufferedWriter, BytesIO, StringIO, TextIOWrapper]] = None,
    node_attr: Optional[Union[list, bool]] = True,
    edge_attr: Optional[Union[list, bool]] = True,
    encoding: str = "utf-8",
    errors: str = "strict",
) -> Union[str, None]:
    """
    Writes a GDF file from a NetworkX graph object.

    .. seealso::

       The `API Reference <https://networkx-gdf.readthedocs.io/en/stable/api.html>`__
       of the ``networkx_gdf`` package for format details.

    :param G: NetworkX graph object.
    :param object file: File object or string containing path to GDF file. Optional. If ``None``
        (default), returns content as string.
    :param node_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

        * If a ``list``, only the specified attributes will be considered.

        * If ``True``, all node attributes will be considered.

        * If ``False``, no node attributes will be considered.

    :param edge_attr: Accepts a ``list`` or ``bool``. Optional. Default is ``True``.

        * If a ``list``, only the specified attributes will be considered.

        * If ``True``, all edge attributes will be considered.

        * If ``False``, no edge attributes will be considered.
    :param encoding: The encoding of the file. Default is ``'utf-8'``.
        For a list of possible values, see `Python documentation: Standard Encodings
        <https://docs.python.org/3/library/codecs.html#standard-encodings>`__.
    :param errors: The error handling scheme. Default is ``'strict'``.
        For a list of possible values, see `Python documentation: Error Handlers
        <https://docs.python.org/3/library/codecs.html#error-handlers>`__.

    :note: Wrapper function for
        `networkx_gdf.write_gdf
        <https://networkx-gdf.readthedocs.io/en/stable/api.html#networkx_gdf.write_gdf>`__.
    """
    try:
        from networkx_gdf import write_gdf
    except ImportError as e:
        raise ImportError(
            "The `networkx_gdf` package is required to write GDF files. "
            "Please install it via `pip install networkx_gdf`."
        ) from e

    return write_gdf(
        G,
        path=file,
        node_attr=node_attr,
        edge_attr=edge_attr,
        encoding=encoding,
        errors=errors,
    )