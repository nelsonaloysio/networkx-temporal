import gzip
import os.path as osp
from datetime import datetime
from pathlib import Path
from typing import Optional

import networkx as nx
from requests import request

from .generators import generate_block_matrix, generate_community_vector
from .sbm import dynamic_stochastic_block_model
from ..transform import from_static
from ..typing import TemporalDiGraph, TemporalMultiDiGraph

DATA_PATH = Path(__file__).parent.resolve() / "data"


def collegemsg_graph() -> TemporalMultiDiGraph:
    """ Returns the CollegeMsg temporal graph.

    The CollegeMsg dataset [12]_ is a temporal social network representing private
    messages sent between students at the University of California, Irvine.
    Nodes represent students, and a directed edge from node :math:`u` to node :math:`v`
    at time :math:`t` indicates that student :math:`u` sent a message to student :math:`v`
    at time :math:`t`. The dataset spans 1,899 students and 59,835 messages over 193 days.

    Edges have a ``'time'`` attribute indicating the date the message was sent, following
    the ``'YYYY-MM-DD HH:MM'`` format, e.g., ``'2002-04-05 17:30'``.

    .. rubric:: Example

    To load the dataset and :func:`~networkx_temporal.classes.TemporalGraph.slice` the graph into
    daily snapshots:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>> from datetime import datetime
        >>>
        >>> TG = tx.generators.collegemsg_graph()
        >>>
        >>> def to_date(x):
        >>>     # Convert hourly dates to YYYY-MM-DD format, allowing to sort them by day.
        >>>     return datetime.strptime(x.strip(), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
        >>>
        >>> TG = TG.slice(attr="time", apply_func=to_date)
        >>> print(TG)

        TemporalMultiDiGraph (t=193) with 1899 nodes and 59835 edges

    .. [12] Pietro Panzarasa, Tore Opsahl, and Kathleen M. Carley.
        ''Patterns and dynamics of users' behavior and interaction: Network analysis of an
        online community''. Journal of the American Society for Information Science and
        Technology 60.5 (2009): 911-932.
        doi: `10.1002/asi.21015 <https://doi.org/10.1002/asi.21015>`__.

    """
    def to_date(x):
        return datetime.strptime(x.strip(), "%m/%d/%y %I:%M %p").strftime("%Y-%m-%d %H:%M")

    with gzip.open(DATA_PATH / "collegemsg.csv.gz", "r") as f:
        G = nx.read_edgelist(f.readlines()[1:],
                             create_using=nx.MultiDiGraph,
                             data=[("time", str)],
                             delimiter=",",
                             nodetype=int)

    # Convert date attribute "4/5/02 05:30 PM" to "2002-04-05 17:30" for correct sorting.
    nx.set_edge_attributes(
        G,
        {e: to_date(d["time"]) for e, d in G.edges.items()},
        "time"
    )

    return from_static(G).slice(attr="time", apply_func=lambda x: x.split()[0])


def example_sbm_graph() -> TemporalMultiDiGraph:
    """ Returns a synthetic graph generated with the stochastic block model.

    This function employs the :func:`~networkx_temporal.generators.dynamic_stochastic_block_model`
    to create a temporal graph with 75 nodes divided into 3 communities, evolving over 3 snapshots.
    Edges between nodes within the same community are created with a probability of 20%, or 1%
    among different communities.

    .. note::

        This function is primarily intended for testing and demonstration purposes.

    .. rubric:: Example

    To load the dataset:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.example_sbm_graph()
        >>> print(TG)

        TemporalMultiDiGraph (t=3) with 75 nodes and 563 edges

    Which corresponds to the graph generated with
    :func:`~networkx_temporal.generators.dynamic_stochastic_block_model` as follows:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> k = 3         # Number of communities.
        >>> n = 25        # Number of nodes.
        >>> t = 3         # Number of snapshots.
        >>> p_in = 0.2    # Probability of within-community edges.
        >>> p_out = 0.01  # Probability of between-community edges.
        >>>
        >>> B = tx.generate_block_matrix(k, p=p_in, q=p_out)
        >>> z = tx.generate_community_vector(nodes=n, k=k)
        >>> TG = tx.dynamic_stochastic_block_model(B, z, t=t, isolates=False, seed=10)

    .. code-block:: python

        >>> tx.draw(TG,
        ...         figsize=(6, 2),
        ...         layout="spring",
        ...         node_size=50,
        ...         temporal_node_color=tx.get_node_attributes(TG, "community"),
        ...         with_labels=False)

    .. image:: ../../assets/figure/generators/example_sbm_graph.png
       :align: center
    """
    B = generate_block_matrix(k=3, p=0.2, q=0.01)
    z = generate_community_vector(nodes=25, k=3)
    TG = dynamic_stochastic_block_model(B, z, t=3, isolates=False, seed=10)
    return TG


def pubmed_graph(data: bool = False, root: Optional[str] = None) -> TemporalDiGraph:
    """ Returns the PubMed temporal graph.

    The PubMed [13]_ temporal [14]_ dataset is a citation network where nodes represent scientific
    papers in the PubMed database, and a directed edge from node :math:`u` to node :math:`v` at
    time :math:`t` indicates that paper :math:`u` cited paper :math:`v` at time :math:`t`.
    The dataset spans 19,717 papers and 44,335 citations over a period of 42 years, from 1967
    (:math:`t=0`) to 2010 (:math:`t=42`). The first cited paper is from 1964.

    Edges have a ``'time'`` attribute indicating the year the citation occurred as an integer
    value, while nodes have an associated ``'label'`` attribute representing the paper's research
    topic, among three possible classes
    If ``data`` is set to ``True``, nodes will have additional attributes corresponding to the
    TF-IDF scores of specific words in each paper's abstract. If the features file is not present
    in the specified ``root`` directory, it will be downloaded from a remote repository.

    .. rubric:: Example

    To load the dataset already sliced into yearly snapshots:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.pubmed_graph()
        >>>
        >>> print(TG)

        TemporalDiGraph (t=42) with 19717 nodes and 44335 edges

    .. [13] Passos, N.A.R.A., Carlini, E., Trani, S. (2024).
        ''Deep Community Detection in Attributed Temporal Graphs: Experimental Evaluation of
        Current Approaches''. In Proceedings of the 3rd GNNet Workshop: Graph Neural Networking
        Workshop. The 20th International Conference on emerging Networking EXperiments and
        Technologies (CoNEXT 2024), Los Angeles, CA, USA.
        doi: `10.1145/3694811.3697822 <https://doi.org/10.1145/3694811.3697822>`__.

    .. [14] Namata et al. (2012).
        ''Query-driven Active Surveying for Collective Classification''.
        Workshop on Mining and Learning with Graphs (MLG), Edinburgh, Scotland, UK, 2012.
        url: `people.cs.vt.edu/~bhuang/papers/namata-mlg12.pdf
        <https://people.cs.vt.edu/~bhuang/papers/namata-mlg12.pdf>`__.

    :param data: If ``True``, loads additional node features from file.
    :param root: Directory where to store the additional node features file if
        not already present. If ``None``, uses the default data directory.
    """
    with gzip.open(DATA_PATH / "pubmed-edges.csv.gz", "r") as f:
        G = nx.read_edgelist(f.readlines()[1:],
                             create_using=nx.DiGraph,
                             data=[("time", int)],
                             delimiter=",",
                             nodetype=str)

    with gzip.open(DATA_PATH / "pubmed-nodes.csv.gz", "rt") as f:
        nx.set_node_attributes(G,
                               {line.split(",")[0]: int(line.strip().split(",")[1])
                                for line in f.readlines()[1:]},
                               "label")

    if data:
        Root = Path(root).resolve() if root else DATA_PATH
        filename = Root / "pubmed-features.csv.gz"
        # Download features if file does not exist.
        if not osp.exists(filename):
            _download_pubmed_features(filename)
        # Load additional node features from file.
        # Skip first column (node ID): id,feat_0,feat_1,...
        # Each feature is a float value or 0 if empty.
        with gzip.open(filename, "rt") as f:
            attrs = f.readline().strip().split(",")[1:]
            node_attr = {
                line.split(",")[0]: {
                    key: float(value if value else 0)
                for key, value in zip(attrs, line.strip().split(",")[1:])
            }
            for line in f.readlines()
        }
        nx.set_node_attributes(G, node_attr)

    return from_static(G).slice(attr="time")


def _download_pubmed_features(filename: str) -> None:
    """ Downloads the PubMed node features file to the specified root directory. """
    url = "https://github.com/" \
    "nelsonaloysio/networkx-temporal/raw/refs/heads/development/extra/data/pubmed-features.csv.gz"
    r = request("GET", url, stream=True, timeout=15)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        raise RuntimeError(f"Error {r.status_code}: failed to download file from {url}")
