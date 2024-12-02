#!/usr/bin/env python

import gzip
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import networkx_temporal as tx
import pandas as pd

FILE = "collegemsg.csv.gz"


def test_collegemsg():
    """ Test for College Message dataset. """
    # https://stackoverflow.com/questions/72976127/how-to-create-a-temporal-network-using-networkx

    # First two lines from file:
    # Source,Target,Timestamp
    # 1,2,4/15/04 2:56 PM
    with gzip.open(FILE, "r") as f:
        G = nx.read_edgelist(f.readlines()[1:],
                             create_using=nx.MultiDiGraph,
                             data=[("Timestamp", str)],
                             delimiter=",",
                             nodetype=int)

    print(f"{G} (mean node degree: {2*G.size()/G.order():.2f})")

    # Convert dates to YYYY-MM-DD format, allowing to sort them correctly.
    to_date = lambda x: datetime\
                        .strptime(x.strip(), "%m/%d/%y %I:%M %p")\
                        .strftime("%Y-%m-%d")

    TG = tx.from_static(G)

    TG = TG.slice(attr="Timestamp",
                  level="edge",
                  apply_func=to_date)

    print(TG)

    t = TG.order().index(max(TG.order()))

    print(f"t={t} ({TG.names[t]}) has V={TG[t].order()} nodes and E={TG[t].size()} edges")

    df = pd.DataFrame({"nodes": TG.order(),
                       "edges": TG.size(),
                       "max_in_deg": [
                            max(d[1] for d in deg) for deg in TG.in_degree()],
                       "max_out_deg": [
                            max(d[1] for d in deg) for deg in TG.out_degree()],
                       "mean_deg": [
                            sum(d[1] for d in deg)/len(deg) for deg in TG.degree()]})

    print(df.describe().iloc[1:].round(2))

    fig, ax = plt.subplots(figsize=(7, 6), nrows=2, ncols=1, constrained_layout=True)

    df.index = TG.names

    df.iloc[:, :2].plot(ax=ax[0], color=["#1f77b4cc", "#ff7f0ecc"])
    df.iloc[:, 2:4].plot(ax=ax[1], color=["#2ca02ccc", "#d62728cc"])

    ax[0].legend(labels=["Total nodes", "Total edges"])
    ax[0].set_title(f"Network order, size, and node degree centrality over time ($t$={len(TG)} days)")
    ax[0].set_xticklabels([])

    ax[1].legend(labels=["Max. in-degree", "Max. out-degree"])
    ax[1].set_xlabel("Date")
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=10)

    for ax_ in ax:
        ax_.grid(color="#cccccc", linestyle="dotted", linewidth=1)
        ax_.set_xticklabels(ax_.get_xticklabels(), rotation=10)
        ax_.set_xlim((0, df.shape[0]))
        ax_.set_ylabel("Value")

    fig.savefig("collegemsg.png")


if __name__ == "__main__":
    test_collegemsg()
