from typing import Optional, Union

import networkx as nx
from networkx.classes.reportviews import (
    DegreeView,
    DiDegreeView,
    MultiDegreeView,
    DiMultiDegreeView,
)

from ..typing import TemporalGraph, StaticGraph, Literal
from ..utils import is_static_graph


def centralization(G: StaticGraph, centrality: Union[list, dict], scalar: Union[int, float] = None) -> float:
    """
    Returns graph centralization for each snapshot.

    Centralization [1]_ is defined as the sum of differences between the most central node's
    centrality and each of the other nodes' centralities, divided by the maximum theoretical sum of
    values in a graph with the same properties, such as order, size, and edge directionality.
    It is calculated as:

    .. math::

        C(G) = \\frac
        {\\sum_{i \\in V}\\big(\\text{centrality}_{\\text{max}} - \\text{centrality}(i) \\big)}
        {\\text{centrality}^\\star},

    where :math:`\\text{centrality}_{\\text{max}}` is the maximum centrality of a graph :math:`G`,
    :math:`\\text{centrality}(i)` is the centrality of node :math:`i \\in V`,
    and :math:`\\text{centrality}^\\star` is the maximum theoretical sum of values
    in a similar graph.

    .. seealso::

        The `Algorithms and metrics → Centralization
        <../examples/metrics.html#centralization>`__
        page for an example of usage.

    .. [1] Freeman, L.C. (1979).
       Centrality in Social Networks I: Conceptual Clarification.
       Social Networks 1, 215--239.
       doi: `10.1016/0378-8733(78)90021-7 <https://doi.org/10.1016/0378-8733(78)90021-7>`__

    :param centrality: List or dictionary of node centralities.
    :param scalar: Scalar value for normalization. Optional.
    """
    if isinstance(centrality, (DegreeView, DiDegreeView, MultiDegreeView, DiMultiDegreeView)):
        centrality = [d for n, d in centrality]

    assert type(centrality) in (list, dict),\
        f"Invalid `centrality` type ({type(centrality)}): expects a list or dictionary."
    assert scalar is None or type(scalar) in (int, float),\
        f"Invalid `scalar` type ({type(scalar)}): expects an integer or float."

    if isinstance(centrality, dict):
        centrality = list(centrality.values())

    max_centrality = max(centrality)
    centralization = sum(max_centrality - c for c in centrality)

    if scalar:
        centralization /= scalar

    return float(centralization)


def degree_centralization(TG: Union[TemporalGraph, StaticGraph], selfloops: Optional[bool] = None) -> float:
    """
    Returns degree centralization for each snapshot.

    Centralization [1]_ is the sum of differences between the centrality of the most central node
    and each of the other nodes' centralities, divided by the maximum theoretical
    sum of values in a graph with the same properties.
    In case of degree centralization [2]_, this corresponds to a `star graph
    <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.star_graph.html>`__,
    i.e., a graph with one node connected to all other nodes. The maximum degree of a star
    graph without self-loops is equal to :math:`|V|-1`, where :math:`|V|` is the
    :func:`~networkx_temporal.graph.TemporalGraph.order` of the graph.

    The degree centralization :math:`C_\\text{deg}` of a graph :math:`G` without self-loops
    corresponds to:

    .. math::

        C_\\text{deg}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{deg}_{\\text{max}} - \\text{deg}(i) \\big)}
        {(|V|-1)(\\text{deg}^\\star_{\\text{max}}-1)},

    where :math:`\\text{deg}_{\\text{max}}` is the highest degree in :math:`G`,
    :math:`\\text{deg}(i)` is the degree of node :math:`i \\in V`,
    :math:`|V|` is the number of nodes,
    and :math:`\\text{deg}^\\star_{\\text{max}}` is the maximum node degree in a
    star graph.

    .. seealso::

        The `Algorithms and metrics → Degree centralization
        <../examples/metrics.html#degree-centralization>`__
        page for an example of usage.

    .. [2] See: `igraph R manual pages - Centralization of a graph
       <https://igraph.org/r/doc/centralize.html>`__
       (package version 1.3.5).

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param bool selfloops: If ``True``, self-loops are considered in the calculation.
        If ``False``, self-loops are ignored. Default is ``None`` (auto-detect).
    """
    return _degree_centralization(TG, "degree", selfloops=selfloops)


def in_degree_centralization(TG: Union[TemporalGraph, StaticGraph], selfloops: Optional[bool] = None) -> float:
    """
    Returns in-degree centralization for each snapshot.

    Centralization [1]_ is the sum of differences between the centrality of the most central node
    and each of the other nodes' centralities, divided by the maximum theoretical
    sum of values in a graph with the same properties.
    In case of in-degree centralization [2]_, this corresponds to a `star graph
    <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.star_graph.html>`__,
    i.e., a graph with one node connected to all other nodes. The maximum in-degree of a star
    graph without self-loops is equal to :math:`|V|-1`, where :math:`|V|` is the
    :func:`~networkx_temporal.graph.TemporalGraph.order` of the graph.

    The in-degree centralization :math:`C_\\text{in}` of a graph :math:`G` without self-loops
    corresponds to:

    .. math::

        C_\\text{in}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{deg}_{\\text{in max}} - \\text{deg}_{\\text{in}}(i) \\big)}
        {(|V|-1)(\\text{deg}^\\star_{\\text{in max}})},

    where :math:`\\text{deg}_{\\text{in max}}` is the highest in-degree in :math:`G`,
    :math:`\\text{deg}_{\\text{in}}(i)` is the in-degree of node :math:`i \\in V`,
    :math:`|V|` is the number of nodes,
    and :math:`\\text{deg}^\\star_{\\text{in max}}` is the maximum node in-degree in a
    star graph.

    .. seealso::

        The `Algorithms and metrics → Degree centralization
        <../examples/metrics.html#degree-centralization>`__
        page for an example of usage.

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param bool selfloops: If ``True``, self-loops are considered in the calculation.
        If ``False``, self-loops are ignored. Default is ``None`` (auto-detect).
    """
    return _degree_centralization(TG, "in_degree", selfloops=selfloops)


def out_degree_centralization(TG: Union[TemporalGraph, StaticGraph], selfloops: Optional[bool] = None) -> float:
    """
    Returns out-degree centralization for each snapshot.

    Centralization [1]_ is the sum of differences between the centrality of the most central node
    and each of the other nodes' centralities, divided by the maximum theoretical
    sum of values in a graph with the same properties.
    In case of out-degree centralization [2]_, this corresponds to a `star graph
    <https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.star_graph.html>`__,
    i.e., a graph with one node connected to all other nodes. The maximum out-degree of a star
    graph without self-loops is equal to :math:`|V|-1`, where :math:`|V|` is the
    :func:`~networkx_temporal.graph.TemporalGraph.order` of the graph.

    The out-degree centralization :math:`C_\\text{out}` of a graph :math:`G` without self-loops
    corresponds to:

    .. math::

        C_\\text{out}(G) = \\frac{\\sum_{i \\in V}
        \\big(\\text{deg}_{\\text{out max}} - \\text{deg}_{\\text{out}}(i) \\big)}
        {(|V|-1)(\\text{deg}^\\star_{\\text{out max}})},

    where :math:`\\text{deg}_{\\text{out max}}` is the highest out-degree in :math:`G`,
    :math:`\\text{deg}_{\\text{out}}(i)` is the out-degree of node :math:`i \\in V`,
    :math:`|V|` is the number of nodes,
    and :math:`\\text{deg}^\\star_{\\text{out max}}` is the maximum node out-degree in a
    star graph.

    .. seealso::

        The `Algorithms and metrics → Degree centralization
        <../examples/metrics.html#degree-centralization>`__
        page for an example of usage.

    :param object TG: A :class:`~networkx_temporal.graph.TemporalGraph` or static graph object.
    :param bool selfloops: If ``True``, self-loops are considered in the calculation.
        If ``False``, self-loops are ignored. Default is ``None`` (auto-detect).
    """
    return _degree_centralization(TG, "out_degree", selfloops=selfloops)


def _degree_centralization(
    TG: Union[TemporalGraph, StaticGraph],
    degree: Literal["degree", "in_degree", "out_degree"],
    selfloops: Optional[bool] = None,
):

    assert type(degree) == str,\
        f"Invalid `degree` type ({type(degree)}): expects a string: 'degree', 'in_degree', or 'out_degree'."
    assert degree in ("degree", "in_degree", "out_degree"), \
        f"Invalid `degree`: expects 'degree', 'in_degree', or 'out_degree'."

    if selfloops is None:
        selfloops = any(
            nx.number_of_selfloops(G) > 0
            for G in ([TG] if is_static_graph(TG) else TG)
        )

    minimum = 0 if degree in ("in_degree", "out_degree") else 1

    dc = [
        centralization(
            G,
            centrality=[d for n, d in getattr(G, degree)()],
            scalar=sum((G.order() - (0 if selfloops else 1)) - minimum for n in range(G.order()-1)),
        )
        for G in ([TG] if is_static_graph(TG) else TG)
    ]

    return dc[0] if is_static_graph(TG) else dc
