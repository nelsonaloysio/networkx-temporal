from typing import Union


def is_temporal_graph(obj) -> bool:
    """
    Returns whether an object is a temporal graph.

    :param obj: Object to be tested.
    """
    from . import TemporalBase
    return issubclass(type(obj), TemporalBase)
