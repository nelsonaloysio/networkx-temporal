from typing import Optional, Union

from ..classes import temporal_graph
from ..typing import StaticGraph, TemporalGraph


def read_hif(
    filepath: str,
    directed: bool = None,
    multigraph: bool = None,
    create_using: Optional[Union[TemporalGraph, StaticGraph]] = None,
):
    """
    Returns a :class:`~networkx_temporal.classes.TemporalGraph` from HIF JSON file.

    The Hypergraph Interchange Format (HIF) standard [1] provides a common framework for
    higher-order networks for seamless data exchange between higher-order network libraries, and
    establishes a direct mapping between the Hypergraph and Bipartite Graph representations.

    .. note::

        Requires the `nx_hif (PyPI) <https://pypi.org/project/nx_hif>`__ package installed,
        imported on function call.

    .. [1] Martín Coll et al. (2025). ''Hypergraph Interchange Format (HIF).'' Zenodo.
           doi: `10.5281/zenodo.15802759 <https://doi.org/10.5281/zenodo.15802759>`__.

    :param filepath: Path to the HIF JSON file.
    :param directed: Whether the graph is directed.
    :param multigraph: Whether the graph is a multigraph.
    :param create_using: Graph type to create.
    """
    from nx_hif.readwrite import read_hif

    H = read_hif(filepath)
    TG = temporal_graph(directed=directed, multigraph=multigraph, create_using=create_using)

    for x, d in H.nodes(data=True):
        if d["bipartite"] == 1:
            for n in H[x]:
                TG.add_edge(n, x, **d)

    return TG
