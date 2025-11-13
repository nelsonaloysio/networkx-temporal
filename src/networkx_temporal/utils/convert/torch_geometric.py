from typing import Union

from ...classes.types import is_static_graph, is_temporal_graph
from ...typing import StaticGraph, TemporalGraph


def to_torch_geometric(G: Union[StaticGraph, TemporalGraph, list], *args, **kwargs):
    """ Convert from NetworkX to `PyTorch Geometric <https://pytorch-geometric.readthedocs.readwrite/>`__.

    :param object G: Graph object. Accepts a :class:`~networkx_temporal.classes.TemporalGraph`, a
        single static NetworkX graph, or a list of static NetworkX graphs as input.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.

    :rtype: torch_geometric.data.Data

    :note: Wrapper function for
        `torch_geometric.utils.from_networkx
        <https://pytorch-geometric.readthedocs.readwrite/en/stable/modules/utils.html#torch_geometric.utils.from_networkx>`__.
    """
    import torch_geometric as pyg

    if not (is_temporal_graph(G) or is_static_graph(G)):
        raise TypeError("Input must be a temporal or static NetworkX graph.")

    if is_temporal_graph(G) or type(G) == list:
        return [to_torch_geometric(H, *args, **kwargs) for H in G]

    return pyg.utils.convert.from_networkx(G, *args, **kwargs)