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

    The Fedivertex (or Fediverse) [15]_ dataset contains temporal data of the interactions between
    users of several federated decentralized social media platforms, such as Mastodon.

    .. rubric:: Example

    To load the ``follow`` interactions between users of the Peertube platform between February 3,
    2025 and June 17, 2025 into a :class:`~networkx_temporal.typing.TemporalDiGraph` object:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.fediverse_graph(
        ...     "peertube", "follow", date=("20250203", "20250617")
        ... )
        >>> print(TG)

        TemporalDiGraph (t=20) with 1157 nodes and 310695 edges

    :param software: Federated social media platform to load.
    :param graph_type: Type of interaction graph to load.
    :param index: Optional tuple of start and end indices of snapshots to load.
    :param date: Optional tuple of start and end dates of snapshots to load.
    :param disable_tqdm: If ``True``, disables the progress bar. Default is ``False``.
    :param light_version: If ``True``, loads a smaller version of the dataset. Default is ``True``.

    :note: Wrapper for the ``GraphLoader`` class from
        `fedivertex <https://pypi.org/project/fedivertex/>`__ (PyPI).

    .. [15] Kaggle. ''Fedivertex: The Fediverse Graph Dataset''.
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