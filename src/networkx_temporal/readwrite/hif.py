from typing import Optional, Union

from ..typing import StaticGraph, TemporalGraph


def read_hif(
    filepath: str,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[Union[TemporalGraph, StaticGraph]] = None,
):
    """
    Returns a :class:`~networkx_temporal.classes.TemporalGraph` from HIF JSON file.

    The Hypergraph Interchange Format (HIF) standard [1]_ provides a common framework for
    higher-order networks for seamless data exchange between higher-order network libraries, and
    establishes a direct mapping between the Hypergraph and Bipartite Graph representations.

    .. [1] Martín Coll et al. (2025). ''Hypergraph Interchange Format (HIF).'' Zenodo.
           doi: `10.5281/zenodo.15802759 <https://doi.org/10.5281/zenodo.15802759>`__.

    .. note::

        Requires the `nx_hif (PyPI) <https://pypi.org/project/nx_hif>`__ package installed,
        imported on function call.

    :param filepath: Path to the HIF JSON file.
    :param directed: Whether the graph is directed.
    :param multigraph: Whether the graph is a multigraph.
    :param create_using: Graph type to create.
    """
    from ..classes import temporal_graph

    # check python version
    try:
        import nx_hif.readwrite as _hif

    except ImportError as e:
        raise ImportError(
            "The `nx_hif` package is required to read HIF files. "
            "Please install it via `pip install nx_hif` (Python >= 3.12)."
        ) from e

    # HG := (V, E, I)
    HG = _hif.read_hif(filepath)
    # TG = temporal_graph(directed=directed, multigraph=multigraph, create_using=create_using)
    return HG
