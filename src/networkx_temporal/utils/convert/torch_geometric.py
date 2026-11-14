from typing import Union

from ...classes.types import is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_torch_geometric(graph: Union[StaticGraph, TemporalGraph], *args, **kwargs):
    """ Convert from NetworkX to `PyTorch Geometric <https://pytorch-geometric.readthedocs.io/>`__.

    :param object graph: A :class:`~networkx_temporal.classes.TemporalGraph` or static NetworkX graph
        object.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: torch_geometric.data.Data

    :note: Wrapper function for
        `torch_geometric.utils.from_networkx
        <https://pytorch-geometric.readthedocs.io/en/stable/modules/utils.html#torch_geometric.utils.from_networkx>`__.
    """
    import torch_geometric as pyg

    if is_temporal_graph(graph):
        return [to_torch_geometric(g, *args, **kwargs) for g in graph]

    return pyg.utils.convert.from_networkx(graph, *args, **kwargs)