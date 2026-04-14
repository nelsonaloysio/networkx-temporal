from typing import Optional, Tuple

from ...typing import TemporalDiGraph


def fediverse_graph(
    software: str,
    graph_type: str,
    index: Optional[Tuple[int, int]] = None,
    date: Optional[Tuple[str, str]] = None,
    disable_tqdm: bool = False,
    light_version: bool = True,
) -> TemporalDiGraph:
    """ Returns a temporal graph of interactions between users of a federated social media platform.

    The Fediverse dataset [15]_ contains temporal graphs of interactions between users of 7
    different federated decentralized social media platforms (i.e., Mastodon, Peertube, Pixelfed,
    Friendica, Misskey, Hubzilla, and Lemmy).

    Implementation relies on the ``GraphLoader`` class from the
    `fedivertex <https://pypi.org/project/fedivertex/>`__ (PyPI) package.

    .. rubric:: Example

    Loading the temporal graph of ``follow`` interactions between users of the Peertube platform
    between February 3, 2025 and June 17, 2025:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.fediverse_graph(
        ...     "peertube", "follow", date=("20250203", "20250617")
        ... )
        >>> print(TG)

        TemporalDiGraph (t=20) with 1157 nodes and 310695 edges

    .. [15] Kaggle: ''Fedivertex Graph Dataset''.
        url: `kaggle.com/datasets/marcdamie/fediverse-graph-dataset/data
        <https://www.kaggle.com/datasets/marcdamie/fediverse-graph-dataset/data>`__.
    """
    try:
        from fedivertex import GraphLoader
    except ImportError as e:
        raise ImportError(
            "The `fedivertex` package is required to load Fediverse graphs. "
            "Please install it via `pip install fedivertex`."
        ) from e

    loader = GraphLoader(light_version=light_version)

    TG = loader.get_temporal_graph(
        software=software,
        graph_type=graph_type,
        index=index,
        date=date,
        disable_tqdm=disable_tqdm,
    )
    return TG