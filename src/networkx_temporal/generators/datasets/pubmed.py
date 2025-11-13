import gzip
import os.path as osp
import urllib
from pathlib import Path
from typing import Optional, Union
import zipfile

import networkx as nx

from ...transform import from_static
from ...typing import TemporalDiGraph

DATA_PATH = Path(__file__).parent.resolve() / "pubmed"

DATA_URL = "https://zenodo.org/records/17860933/files/pubmed-features.csv.zip"


def pubmed_graph(features: Optional[Union[bool, str]] = False) -> TemporalDiGraph:
    """ Returns the PubMed temporal graph.

    The PubMed [13]_ temporal [14]_ dataset is a citation network where nodes represent scientific
    papers in the PubMed database, and a directed edge from node :math:`u` to node :math:`v` at
    time :math:`t` indicates that paper :math:`u` cited paper :math:`v` at time :math:`t`.
    The dataset spans 19,717 papers and 44,335 citations over a period of 42 years, from 1967
    (:math:`t=0`) to 2010 (:math:`t=41`). The first cited paper is from 1964.

    Edges have a ``'time'`` attribute indicating the year the citation took place, starting from
    1967, while nodes have an associated ``'label'`` attribute representing the paper's research
    topic, among three possible classes
    If ``features`` is ``True``, nodes will have additional attributes corresponding to the
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

    .. [13] Namata et al. (2012).
        ''Query-driven Active Surveying for Collective Classification''.
        Workshop on Mining and Learning with Graphs (MLG), Edinburgh, Scotland, UK, 2012.
        url: `people.cs.vt.edu/~bhuang/papers/namata-mlg12.pdf
        <https://people.cs.vt.edu/~bhuang/papers/namata-mlg12.pdf>`__.

    .. [14] Passos, N.A.R.A., Carlini, E., Trani, S. (2024).
        ''Deep Community Detection in Attributed Temporal Graphs: Experimental Evaluation of
        Current Approaches''. In Proceedings of the 3rd GNNet Workshop: Graph Neural Networking
        Workshop. The 20th International Conference on emerging Networking EXperiments and
        Technologies (CoNEXT 2024), Los Angeles, CA, USA.
        doi: `10.1145/3694811.3697822 <https://doi.org/10.1145/3694811.3697822>`__.

    :param features: If ``True``, loads additional node features from file.
        Allows passing a string pointing to the directory where the `pubmed-features.csv.gz
        <https://github.com/nelsonaloysio/networkx-temporal/raw/refs/heads/development/extra/data/pubmed-features.csv.gz>`__
        file is located. If the file is not found, it will be downloaded automatically.
        Default is ``False``.

    :note: Dataset and files available from `Zenodo <https://doi.org/10.5281/zenodo.13932075>`__.
    """
    if features is not None and type(features) not in (bool, str):
        raise TypeError("Argument `features` must be a boolean or string.")

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

    if features:
        path = Path(features if type(features) == str else ".")
        if osp.isdir(path):
            path = path / "pubmed-features.csv.zip"

        # Download features file if it does not exist.
        if not zipfile.is_zipfile(path):
            _download_pubmed_features(path.resolve())

        # Load additional node features from file.
        # Skip first column (node ID): id,feat_0,feat_1,...
        # Each feature is a float value, zero if empty in file.
        with zipfile.ZipFile(path, "r") as zf:
            with zf.open("pubmed-features.csv", "r") as f:
                lines = f.read().decode("utf-8").splitlines()
                attrs = lines[0].strip().split(",")[1:]  # Skip the first column (node ID).
                node_attr = {
                    line.split(",")[0]: {
                        key: float(value if value else 0)
                        for key, value in zip(attrs, line.strip().split(",")[1:])
                    }
                    for line in lines[1:]  # Skip header.
                }
        nx.set_node_attributes(G, node_attr)

    TG = from_static(G)
    TG = TG.slice(attr="time")
    TG.name = "PubMed"
    return TG


def _download_pubmed_features(filepath: str) -> None:
    """ Downloads the PubMed node features file to root directory. """
    try:
        with open(filepath, "wb") as f:
            f.write(urllib.request.urlopen(DATA_URL, timeout=15).read())
    except Exception as e:
        raise RuntimeError(f"{e}: Failed to download PubMed features file from {DATA_URL}") from e
