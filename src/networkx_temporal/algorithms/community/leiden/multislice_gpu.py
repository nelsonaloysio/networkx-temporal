from warnings import warn

from typing import List, Union
from ....typing import TemporalGraph, StaticGraph


def leiden_multislice_gpu(
    graph: Union[TemporalGraph, StaticGraph],
    # offsets: Optional[List[int]] = None,
    # gamma: float = 1.0,
    # weight: Optional[str] = "weight",
    # interslice_weight: Optional[float] = 1.0,
    # max_iter: int = 500,
    # max_sweeps: int = 100,
    # refine: bool = True,
    # seed: Optional[int] = None,
    **kwargs
) -> List[List[int]]:
    """ Parallelized multislice Leiden algorithm on GPU.\n:meta private:
    """
    warn(
        "The `leiden_multislice_gpu` function is deprecated in favor of  `leiden_communities"
        "(..., backend='cupy', device='gpu')` and will be removed in a future release.",
        DeprecationWarning
    )
    from . import _leiden_communities_cupy
    return _leiden_communities_cupy(graph, **kwargs)
