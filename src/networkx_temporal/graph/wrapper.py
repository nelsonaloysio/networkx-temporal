from functools import wraps
from typing import Callable

from ..typing import TemporalGraph


def wrapper(cls: TemporalGraph, name: str) -> Callable:
    """
    Return a wrapper function for methods inherited from a static graph.

    This wrapper function is used to handle the case where the method returns
    different booleans for different graphs in the temporal graph. It combines
    the results from all graphs in the temporal graph and returns a single result.
    Otherwise, it returns a list of results from each graph.

    :param cls: Temporal graph class.
    :param name: Method name to decorate.
    """
    @wraps(getattr(cls[0], name))
    def _wrapper(*args, **kwargs):
        returns = list(G.__getattribute__(name)(*args, **kwargs) for G in cls)
        if all(r is None for r in returns):
            return None
        if all(r is True for r in returns):
            return True
        if all(r is False for r in returns):
            return False
        return returns
    return _wrapper
