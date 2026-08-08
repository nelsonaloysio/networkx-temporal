from pathlib import Path
from typing import Optional
import zipfile

import networkx as nx
import pandas as pd

from ....classes import temporal_graph
from ....typing import TemporalMultiDiGraph
from ....utils import combine_snapshots, get_node_attributes, partition_nodes

DATA_PATH = Path(__file__).parent.resolve()


def travian_graph(
    edgetype: Optional[str] = None,
    alliances_only: bool = False,
    drop_duplicates: bool = False,
    ) -> TemporalMultiDiGraph:
    """ Returns the Travian temporal graph.

    The Travian dataset [16]_ is a graph representing interactions between players in the online
    game Travian. Nodes represent the players, and directed edges their interactions among
    three types: attacks, messages, and trades. The dataset spans a period of 30 days starting from
    December 1, 2009 to December 30, 2009, with daily snapshots and edge timestamps in seconds.

    Some nodes have an ``'alliance'`` attribute representing the player's alliance, while edges
    have ``'date'``, ``'time'``, and ``'edgetype'`` attributes representing the original dataset
    split, interaction time, and interaction type, respectively. As alliances are dynamic, players
    may change or leave their alliances at any point, or may not belong to any alliance at all.

    Note that the original dataset contains duplicate edges (same source, target, and timestamp),
    which may be removed by setting ``drop_duplicates=True``. Nodes without an ``'alliance'`` or
    in isolated alliances may also be removed by setting ``alliances_only=True``.

    .. rubric:: Example

    To load the dataset already sliced into daily snapshots:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.generators.travian_graph()
        >>> print(TG)

        TemporalMultiDiGraph named 'Travian' (t=30) with 4612 nodes and 1338110 edges

    Or, considering only nodes that belong to an alliance with at least one other member:

    .. code-block:: python

        >>> TG = tx.generators.travian_graph(alliances_only=True)

        TemporalMultiDiGraph named 'Travian' (t=30) with 2732 nodes and 1004769 edges

    .. [16] Hajibagheri, A. et al. (2015).
        ''Conflict and Communication in Massively-Multiplayer Online Games''.
        In Proceedings of the International Conference on Social Computing, Behavioral-Cultural
        Modeling, and Prediction. Washington, DC, USA, March 31-April 3, 2015.
        pdf: `ial.eecs.ucf.edu/pdf/Sukthankar-SBP2015.pdf
        <https://ial.eecs.ucf.edu/pdf/Sukthankar-SBP2015.pdf>`__.

    :param edgetype: Filter edges by type among ``'attacks'``, ``'messages'``, and ``'trades'``.
        If ``None``, loads all edges (default).
    :param alliances_only: Whether to keep only nodes that belong to an alliance.
        If ``True``, removes nodes without an ``'alliance'`` attribute or in isolated alliances.
        Default is ``False``.
    :param duplicates: Whether to keep duplicate edges (same source, target, and timestamp).
        If ``False``, only the first occurrence of each edge is kept. Default is ``True``.

    :note: Original dataset available at: `Intelligent Agents Lab (UCF)
        <https://ial.eecs.ucf.edu/travian-dataset/>`__.
    """
    if edgetype not in ("attacks", "messages", "trades", None):
        raise ValueError("Invalid edge type, expects 'attacks', 'messages', or 'trades' if set.")

    TG = temporal_graph(directed=True, multigraph=True)
    name = f"Travian{f'-{edgetype.capitalize()}' if edgetype else ''}"
    edgetype = (("attacks", "messages", "trades") if edgetype is None else (edgetype,))

    # Build temporal graph snapshots from each csv edge list in zip file.
    for i, et in enumerate(edgetype):
        TG_et = temporal_graph(directed=True, multigraph=True)
        filepath = DATA_PATH / f"travian-{et}.zip"

        with zipfile.ZipFile(filepath, "r") as zf:
            for z in zf.namelist():
                date = "-".join(z.split(".")[0].split("-")[-3:])

                df = pd\
                    .read_csv(zf.open(z), header=None, names=["time", "source", "target"])\
                    .sort_values("time", ascending=True)

                if drop_duplicates:
                    df = df.drop_duplicates()

                G = nx.from_pandas_edgelist(
                    df,
                    source="source",
                    target="target",
                    edge_attr="time",
                    create_using=nx.MultiDiGraph,
                )
                G.name = date

                nx.set_edge_attributes(G, date, "date")
                nx.set_edge_attributes(G, et.rstrip("s"), "edgetype")

                TG_et.add_snapshot(G)

        # Combine same-index snapshots of graphs with different edge types.
        TG = TG_et if i == 0 else combine_snapshots([TG, TG_et])
        TG.index = [G.name for G in TG_et]

    # Load communities into graph.
    with zipfile.ZipFile(DATA_PATH / "travian-communities.zip", "r") as zf:
        for z in zf.namelist():
            date = "-".join(z.split(".")[0].split("-")[-3:])

            with zf.open(z, "r") as f:
                partitions = [
                    [int(x) for x in line.split()]
                    for line in f.read().decode("utf-8").splitlines()[1:]
                ]
                community = {n: i for i, partition in enumerate(partitions) for n in partition}

            nx.set_node_attributes(TG[date], community, "community")

    # Remove nodes without an alliance or in isolated alliances, and remove node isolates.
    if alliances_only:
        community = get_node_attributes(TG, "community")
        partition = partition_nodes(TG, community)
        node_alliance_max = {}
        for t in range(len(TG)):
            for n in community[t]:
                node_alliance_max[n] = max(
                    node_alliance_max.get(n, 0),
                    len(partition[t][community[t][n]])
                )
        nodes_in_alliance = set(
            n for n, alliance_size in node_alliance_max.items() if alliance_size > 1)
        TG.graphs = {
            t: G.subgraph(nodes_in_alliance).copy() for t, G in TG.items()}
        list(G.remove_nodes_from(list(nx.isolates(G))) for G in TG.graphs)

    TG.name = name
    return TG
