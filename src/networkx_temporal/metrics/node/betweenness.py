from functools import reduce
from operator import or_
from typing import Any, Optional, Union


def temporal_betweenness(
    self,
    nbunch: Optional[Any] = None,
    weight: Optional[str] = None
) -> Union[dict, int]:
    """
    Returns temporal node betweenness.

    :param nbunch: One or more nodes to consider. Optional.
    :param weight: Edge attribute key to consider. Optional.
    """
    return