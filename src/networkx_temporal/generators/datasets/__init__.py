from .collegemsg import collegemsg_graph
from .fediverse import fediverse_graph
from .pubmed import pubmed_graph
from .travian import travian_graph

DATASETS = [
    "collegemsg",
    "fediverse",
    "pubmed",
    "travian"
]

__all__ = (
    "collegemsg_graph",
    "fediverse_graph",
    "pubmed_graph",
    "travian_graph",
)