from typing import Optional, Union

import networkx as nx
from networkx.classes.reportviews import (
    DegreeView,
    DiDegreeView,
    MultiDegreeView,
    DiMultiDegreeView,
)

from ..typing import TemporalGraph, StaticGraph, Literal
from ..utils import from_multigraph, is_static_graph


def centralization(centrality: Union[list, dict], scalar: Union[int, float, list, dict] = None) -> float:
    """
    Returns centralization of a graph.

    Centralization [0]_ is defined as the sum of differences between the most central node's
    centrality and each of the other nodes' centralities, divided by the maximum theoretical sum of
    values in a graph with the same properties, such as order, size, and edge directionality.
    It is calculated as:

    .. math::

        C(G) = \\frac
        {\\sum_{i \\in V}\\big(\\text{centrality}_{\\text{max}} - \\text{centrality}(i) \\big)}
        {\\sum_{i \\in V}\\big(\\text{theoretical}_{\\text{max}} - \\text{theoretical}(i) \\big)}

    where
    :math:`\\text{centrality}_{\\text{max}}` is the maximum node centrality in :math:`G`,
    :math:`\\text{centrality}(i)` is the centrality of node :math:`i \\in V`,
    and :math:`{\\text{theoretical}}_{\\text{max}}` and :math:`{\\text{theoretical}}(i)`
    refer to node centralities of a theoretical likewise graph for which the sum of differences
    equals the highest possible ``scalar`` value.

    .. [0] Freeman, L.C. (1979).
       Centrality in Social Networks I: Conceptual Clarification.
       Social Networks 1, 215--239.
       doi: `10.1016/0378-8733(78)90021-7 <https://doi.org/10.1016/0378-8733(78)90021-7>`__

    .. rubric:: Example

    Calculating the degree centralization of a simple graph (no parallel edges, self-loops
    or isolates):

    .. code-block:: python

        >>> import networkx as nx
        >>> import networkx_temporal as tx
        >>>
        >>> G = nx.Graph()
        >>> G.add_edges_from([
        ...     (1, 0),
        ...     (2, 0),
        ...     (3, 0),
        ... ])
        >>>
        >>> centrality = G.degree()  # Node degree values.
        >>> maximum = G.order() - 1  # Highest possible degree.
        >>> minimum = 1              # Minimum possible degree.
        >>>
        >>> # Highest theoretical sum of values in a simple star-like graph.
        >>> scalar = sum(maximum - minimum for n in range(G.order()-1))
        >>>
        >>> tx.centralization(centrality=centrality, scalar=scalar)

        1.0

    Or passing a list of theoretical centrality values instead of calculating it:

    .. code-block:: python

        >>> theoretical_centrality = [3, 1, 1, 1]  # Theoretical degree values.
        >>> tx.centralization(centrality=centrality, scalar=theoretical_centrality)

        1.0

    :param centrality: List or dictionary of node centralities.
    :param scalar: Maximum theoretical sum of values. Accepts a value, list, or dictionary
        with node centrality degrees values. Optional.
    """
    if isinstance(centrality, (DegreeView, DiDegreeView, MultiDegreeView, DiMultiDegreeView)):
        centrality = [d for n, d in centrality]

    assert type(centrality) in (list, dict),\
        f"Invalid `centrality` type ({type(centrality)}): expects a list or dictionary."
    assert scalar is None or type(scalar) in (int, float, list, dict),\
        f"Invalid `scalar` type ({type(scalar)}): expects an integer, float, list or dictionary."

    if isinstance(centrality, dict):
        centrality = list(centrality.values())

    max_centrality = max(centrality)
    centralization = sum(max_centrality - c for c in centrality)

    if scalar:
        if isinstance(scalar, dict):
            scalar = list(scalar.values())
        if isinstance(scalar, list):
            max_theoretical = max(scalar)
            scalar = sum(max_theoretical - s for s in scalar)
        centralization /= scalar

    return float(centralization)


def degree_centralization(
    TG: Union[TemporalGraph, StaticGraph],
    loops: Optional[bool] = None,
    isolates: Optional[bool] = None,
) -> float:
    """
    Returns degree centralization of a graph.

    The degree centralization [2]_ of a graph is the sum of differences between the centrality of
    the most central node and each of the other nodes' centralities, divided by the maximum
    theoretical sum of values in a graph with the same order, size, and edge directionality,
    i.e., a `star graph
    <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.star_graph.html>`__.

    The degree centralization :math:`C_\\text{deg}` of a simple graph without self-loops
    :math:`G` corresponds to:

    .. math::

        C_\\text{deg}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{deg}_{\\text{max}} - \\text{deg}(i) \\big)}
        {(|V|-1)(\\text{deg}^\\star_{\\text{max}} - 1)},

    where :math:`|V|` is the number of nodes,
    :math:`\\text{deg}_{\\text{max}}` is the highest node degree in :math:`G`,
    :math:`\\text{deg}(i)` is the degree of node :math:`i \\in V`,
    and :math:`\\text{deg}^\\star_{\\text{max}} = |V|-1`
    is the maximum theoretical node degree.

    .. [2] See: `igraph R manual pages - Centralization of a graph
       <https://igraph.org/r/doc/centralize.html>`__
       (package version 1.3.5).

    .. note::

       In temporal networks, degree centralization is calculated for each time slice of the graph.

    .. rubric:: Example

    .. code-block:: python

        >>> import networkx as nx
        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.TemporalGraph(2)
        >>> TG[0].add_edges_from([
        ...     (0, 1),
        ...     (0, 2),
        ... ])
        >>> TG[1].add_edges_from([
        ...     (0, 1),
        ...     (1, 2),
        ...     (2, 0),
        ... ])
        >>> tx.degree_centralization(TG)

        [1.0, 0.75]

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param bool loops: If ``True``, self-loops are considered in the calculation.
        Defaults to ``False``.
    :param bool isolates: If ``True``, node isolates are considered in the calculation.
        Defaults to ``False``.
    """
    return _degree_centralization(TG, "degree", loops=loops, isolates=isolates)


def in_degree_centralization(
    TG: Union[TemporalGraph, StaticGraph],
    loops: Optional[bool] = None,
    isolates: Optional[bool] = None,
) -> float:
    """
    Returns in-degree centralization of a graph.

    The in-degree centralization :math:`C_\\text{in}` of a simple graph without self-loops
    :math:`G` corresponds to:

    .. math::

        C_\\text{in}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{in}_{\\text{max}} - \\text{in}(i) \\big)}
        {(|V|-1)(\\text{in}^\\star_{\\text{max}} - 1)},

    where :math:`|V|` is the number of nodes,
    :math:`\\text{in}_{\\text{max}}` is the highest node in-degree in :math:`G`,
    :math:`\\text{in}(i)` is the in-degree of node :math:`i \\in V`,
    and :math:`\\text{in}^\\star_{\\text{max}} = |V|-1`
    is the maximum theoretical node in-degree.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.centralization.degree_centralization` function
        for details on the metric and an example of usage.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param bool loops: If ``True``, self-loops are considered in the calculation.
        Defaults to ``False``.
    :param bool isolates: If ``True``, node isolates are considered in the calculation.
        Defaults to ``False``.
    """
    return _degree_centralization(TG, "in_degree", loops=loops, isolates=isolates)


def out_degree_centralization(
    TG: Union[TemporalGraph, StaticGraph],
    loops: Optional[bool] = None,
    isolates: Optional[bool] = None,
) -> float:
    """
    Returns out-degree centralization of a graph.

    The out-degree centralization :math:`C_\\text{out}` of a simple graph without self-loops
    :math:`G` corresponds to:

    .. math::

        C_\\text{out}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{out}_{\\text{max}} - \\text{out}(i) \\big)}
        {(|V|-1)(\\text{out}^\\star_{\\text{max}} - 1)},

    where :math:`|V|` is the number of nodes,
    :math:`\\text{out}_{\\text{max}}` is the highest node out-degree in :math:`G`,
    :math:`\\text{out}(i)` is the out-degree of node :math:`i \\in V`,
    and :math:`\\text{out}^\\star_{\\text{max}} = |V|-1`
    is the maximum theoretical node out-degree.

    .. seealso::

        The :func:`~networkx_temporal.algorithms.centralization.degree_centralization` function
        for details on the metric and an example of usage.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` or static graph object.
    :param bool loops: If ``True``, self-loops are considered in the calculation.
        Defaults to ``False``.
    :param bool isolates: If ``True``, node isolates are considered in the calculation.
        Defaults to ``False``.
    """
    return _degree_centralization(TG, "out_degree", loops=loops, isolates=isolates)


def _degree_centralization(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    loops: bool = False,
    isolates: bool = False,
) -> Union[float, list]:

    assert degree in ("degree", "in_degree", "out_degree"),\
        f"Invalid `degree`: expects 'degree', 'in_degree', or 'out_degree'."

    if any(G.is_multigraph() for G in ([TG] if is_static_graph(TG) else TG)):
        TG = from_multigraph(TG)

    centralizations = []
    for G in ([TG] if is_static_graph(TG) else TG):
        centrality = getattr(G, degree)()
        maximum = G.order() - 1 if not loops else G.number_of_nodes()
        minimum = 1 if not loops else 0
        scalar = sum(maximum - minimum for n in range(G.order() - 1))
        if loops:
            scalar += G.number_of_selfloops()
        if not isolates:
            scalar -= len(list(nx.isolates(G))) * (maximum - minimum)
        c = centralization(centrality=centrality, scalar=scalar)
        centralizations.append(c)

    return centralizations[0] if is_static_graph(TG) else centralizations
