# networkx-temporal

Python package to build and manipulate temporal NetworkX graphs.

## Requirements

* **Python>=3.7**
* networkx>=2.1
* pandas>=1.1.0

## Install

Package is available to install on [PyPI](https://pypi.org/project/networkx-temporal/):

```bash
pip install networkx-temporal
```

___

## Usage

The code provided as example below is also available as an interactive [Jupyter notebook](https://github.com/nelsonaloysio/networkx-temporal/blob/main/example/notebook.ipynb) ([open on Colab](https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/example/notebook.ipynb)).

### Build temporal graph

The `Temporal{Di,Multi,MultiDi}Graph` class uses NetworkX graphs internally to allow easy manipulation of its data structures:

```python
import networkx_temporal as tx

TG = tx.TemporalDiGraph(t=4)

TG[0].add_edge("a", "b")
TG[1].add_edge("c", "b")
TG[2].add_edge("d", "c")
TG[2].add_edge("d", "e")
TG[2].add_edge("a", "c")
TG[3].add_edge("f", "e")
TG[3].add_edge("f", "a")
TG[3].add_edge("f", "b")
```

```python
from networkx_temporal.tests.example import draw_temporal_graph
draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_8_0.png)

### Slice into temporal bins

Once initialized, a specified number of bins can be returned in a new object of the same type using `slice`:

```python
TGS = TG.slice(bins=2)
draw_temporal_graph(TGS, figsize=(4, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_10_0.png)

By default, created bins are composed of non-overlapping edges and might have uneven size. To balance them, pass `qcut=True`:

```python
TGS = TG.slice(bins=2, qcut=True)
draw_temporal_graph(TGS, figsize=(4, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_12_0.png)

Note that in some cases, `qcut` may not be able to split the graph into the number of bins requested and will instead return the maximum number of bins possible. Other exceptions can be worked around by setting `duplicates=True` to allow duplicate edges in bins, or `rank_first=True` to balance snapshots considering the order in which nodes or edges appear.

### Convert to directed or undirected

We can easily convert the edge directions by calling the same methods available from `network`:

```python
TG.to_undirected()

# TemporalGraph(t=4)
```

```python
TG.to_directed()

# TemporalDiGraph(t=4)
```

___

## Common metrics

All methods implemented by `networkx`, e.g., `degree`, are also available to be executed sequentially on the stored time slices.

A few additional methods that consider all time slices are also implemented for convenience, e.g., `temporal_degree` and `temporal_neighbors`.

### Degree centrality

```python
TG.degree()
# TG.in_degree()
# TG.out_degree()
```


```python
TG.temporal_degree()
# TG.temporal_in_degree()
# TG.temporal_out_degree()
```

Or to obtain the degree of a specific node:

```python
TG[0].degree("a")
# TG[0].in_degree("a")
# TG[0].out_degree("a")
```

```python
TG.temporal_degree("a")
# TG.temporal_in_degree("a")
# TG.temporal_out_degree("a")
```

### Node neighborhoods

```python
TG.neighbors("c")
```

To obtain the temporal neighborhood of a node considering all time steps, use the method `temporal_neighbors`:

```python
TG.temporal_neighbors("c")
```

### Order and size

The temporal order and size are defined as the number of unique nodes and edges, respectively, across all time steps.

```python
TG.order(), TG.size()
```

```python
TG.temporal_order(), TG.temporal_size()
```

Note that we are also able to consider nodes or edges with distinct attributes as not unique by passing `data=True` to `temporal_{order,size}`.

Lastly, to obtain the total (non-unique) number of nodes and edges across all time steps, we may use the `total_order` and `total_size` methods:

```python
TG.total_order(), TG.total_size()  # sum(TG.order()), sum(TG.size())
```

___

## Convert from static to temporal graph

Static graphs can also carry temporal information either in the node- or edge-level attributes.

Slicing a graph into bins usually result in the same number of edges, but a higher number of nodes, as they may appear in more than one snapshot to preserve edge information.

In the example below, we create a static multigraph in which both nodes and edges are attributed with the time step `t` in which they are observed:

```python
import networkx as nx

G = nx.MultiDiGraph()

G.add_nodes_from([
    ("a", {"t": 0}),
    ("b", {"t": 0}),
    ("c", {"t": 1}),
    ("d", {"t": 2}),
    ("e", {"t": 3}),
    ("f", {"t": 3}),
])

G.add_edges_from([
    ("a", "b", {"t": 0}),
    ("c", "b", {"t": 1}),
    ("d", "c", {"t": 2}),
    ("d", "e", {"t": 2}),
    ("a", "c", {"t": 2}),
    ("f", "e", {"t": 3}),
    ("f", "a", {"t": 3}),
    ("f", "b", {"t": 3}),
])
```

### Node-level time attributes

Converting a static graph with node-level temporal data to a temporal graph object (`node_level` considers the source node's time by default when slicing edges):

```python
TG = tx.from_static(G).slice(attr="t", attr_level="node", node_level="source", bins=None, qcut=None)
draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_35_0.png)

Note that considering node-level attributes resulted in placing the edge `(a, c, 2)` in $t=0$ instead, as the source node `a` attribute is set to `t=0`:

```python
G.nodes(data=True)["a"]
```

### Edge-level time attributes

Converting a static graph with edge-level temporal data to a temporal graph object (edge's time applies to both source and target nodes):

```python
TG = tx.from_static(G).slice(attr="t", attr_level="edge", bins=None, qcut=None)
draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_39_0.png)

In this case, considering edge-level attributes results in placing the edge `(a, c, 2)` in $t=2$, as expected.

___

## Transform temporal graph

Once a temporal graph is instantiated, some methods are implemented that allow converting it or returning snaphots, events or unified temporal graphs.

- `to_static`: returns a single graph with all edges and unique nodes, does not support dynamic node attributes;
- `to_unified`: returns a single graph with all edges and non-unique nodes, supports dynamic node attributes;
- `to_snapshots`: returns a list of graphs with all edges and possibly repeated nodes, preserves edge information;
- `to_events`: returns a list of observed events as 3-tuples or 4-tuples

We may convert our graph to a different object type by calling `convert_to` or passing `to={package}`, provided the `package` is locally installed.

Note that the above applies to the `to_static`, `to_snapshots`, and `to_unified` methods only. Supported formats include:

- `dgl`
- `graph_tool` (`gt`)
- `igraph` (`ig`)
- `networx` (`nx`)
- `networkit` (`nk`)
- `torch_geometric` (`pyg`)

```python
tx.convert_to(G, "igraph")
```

### Get static graph

Builds a static or flattened graph containing all the edges found at each time step:

```python
G = TG.to_static()
draw_temporal_graph(G, suptitle="Static Graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_45_0.png)

### Get snapshots

Returns a list of graphs internally stored under `data` in the temporal graph object, which may too be converted by passing `to={package}`:

```python
STG = TG.to_snapshots()
```

### Get unified temporal graph

The unified temporal graph (UTG) is a single graph that contains the original data plus proxy nodes and edge couplings connecting sequential temporal nodes.

```python
UTG = TG.to_unified(add_couplings=True, add_proxy_nodes=False, proxy_nodes_with_attr=True, prune_proxy_nodes=True)  # node_index=G.nodes()
```

```python
nodes = sorted(TG.temporal_nodes())
pos = {node: (nodes.index(node.rsplit("_")[0]), -int(node.rsplit("_")[1])) for node in UTG.nodes()}
draw_temporal_graph(UTG, pos=pos, figsize=(4, 4), connectionstyle="arc3,rad=0.25", suptitle="Unified Temporal Graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_50_0.png)

### Get sequence of events

An event-based temporal graph (ETG) is a sequence of 3- or 4-tuple edge-based events.

* 3-tuples: `(u, v, t)`, where elements are the source node, target node, and time step of the observed event (also known as a stream graph);

* 4-tuples: `(u, v, t, e)`, where `e` is either a positive (1) or negative (-1) unity for edge addition and deletion, respectively.

```python
ETG = TG.to_events()  # stream=True (default)
ETG

# [('a', 'b', 0),
#  ('c', 'b', 1),
#  ('a', 'c', 2),
#  ('d', 'c', 2),
#  ('d', 'e', 2),
#  ('f', 'e', 3),
#  ('f', 'a', 3),
#  ('f', 'b', 3)]
```

```python
ETG = TG.to_events(stream=False)
ETG

# [('a', 'b', 0, 1),
#  ('c', 'b', 1, 1),
#  ('a', 'b', 1, -1),
#  ('a', 'c', 2, 1),
#  ('d', 'c', 2, 1),
#  ('d', 'e', 2, 1),
#  ('c', 'b', 2, -1),
#  ('f', 'e', 3, 1),
#  ('f', 'a', 3, 1),
#  ('f', 'b', 3, 1),
#  ('a', 'c', 3, -1),
#  ('d', 'c', 3, -1),
#  ('d', 'e', 3, -1)]
```

### Convert back to TemporalGraph object

Functions to convert a newly created STG, ETG, or UTG back to a temporal graph object are also implemented.

```python
tx.from_snapshots(STG)
```

```python
tx.from_events(ETG, directed=True, multigraph=True)
```

```python
tx.from_unified(UTG)
```

___

## Detect temporal communities

The [leidenalg](https://leidenalg.readthedocs.io) package implements community detection algorithms on snapshot-based temporal graphs.

Depending on the objectives, temporal community detection may bring significant advantages on what comes to descriptive tasks and post-hoc network analysis.

Let's first use the [Stochastic Block Model](https://networkx.org/documentation/stable/reference/generated/networkx.generators.community.stochastic_block_model.html) to construct a temporal graph of 4 snapshots, in which each of the five clusters of four nodes each continuously mix together:

```python
snapshots = 4   # Temporal snapshots to creaete.
clusters = 5    # Number of clusters/communities.
order = 4       # Nodes in each cluster.
intra = .95     # High probability of intra-community edges.
inter = .05     # Low initial probability of inter-community edges.
change = .25    # Change in intra- and inter-community edges over time.

# Get probabilities for each snapshot.
probs = [[[(intra if i == j else inter) + (t * (change/snapshots) * (-1 if i == j else 1))
            for j in range(clusters)
        ] for i in range(clusters)
    ] for t in range(snapshots)]

# Create graphs from probabilities.
graphs = {}
for t in range(snapshots):
    graphs[t] = nx.stochastic_block_model(clusters*[order], probs[t], seed=10)
    graphs[t].name = t

# Create temporal graph from snapshots.
TG = tx.from_snapshots(graphs)
```

### Static community detection

#### On the static graph (flattened)

Running the Leiden algorithm on the static graph to obtain the community modules fails to retrieve the five communities in the network:

```python
import leidenalg as la

c = plt.cm.tab10.colors

membership = la.find_partition(
    TG.to_static("igraph"),
    la.ModularityVertexPartition,
    n_iterations=-1,
    seed=0,
)

node_color = [c[m] for m in membership.membership]

draw_temporal_graph(TG.to_static(), figsize=(4, 4), node_color=node_color, suptitle="Static Communities")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_61_0.png)

We can plot all four generated snapshots, while keeping the community assignments from the previous run:

```python
draw_temporal_graph(TG, figsize=(12, 4), node_color=node_color, suptitle="Static Communities")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_63_0.png)

Note that running the same algorithm on the unified temporal graph also yields no significant advantages in terms of correctly retrieving the five clusters.

#### On the snapshots (individually)

Running the same algorithm on each of the generated snapshots instead retrieves the correct clusters on the first snapshot only.

Although results may seem initially better, we lose the community indices previously assigned to nodes in previous snapshots, represented by their different colors:

```python
temporal_opts = {}

for t in range(len(TG)):
    membership = la.find_partition(
        TG[t:t+1].to_static("igraph"),
        la.ModularityVertexPartition,
        n_iterations=-1,
        seed=0,
    )
    temporal_opts[t] = {
        "node_color": [c[m] for m in membership.membership]
    }

draw_temporal_graph(TG, nrows=1, ncols=4, figsize=(12, 4), suptitle="Snapshot Communities", temporal_opts=temporal_opts)
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_66_0.png)

#### Temporal community detection

Detecting temporal communities instead allows us to correctly retrieve the clusters in all snapshots, while maintaining their indices/colors over time.

The `interslice_weight` among temporal nodes in a sequence of snapshots defaults to `1.0` in unweighted graphs and may be adjusted accordingly:

```python
temporal_membership, improvement = la.find_partition_temporal(
    TG.to_snapshots("igraph"),
    la.ModularityVertexPartition,
    interslice_weight=1.0,
    n_iterations=-1,
    seed=0,
    vertex_id_attr="_nx_name"
)

temporal_opts = {
    t: {"node_color": [c[m] for m in temporal_membership[t]]}
    for t in range(len(TG))
}

draw_temporal_graph(TG, nrows=1, ncols=4, figsize=(12, 4), suptitle="Temporal Communities", temporal_opts=temporal_opts)
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/example/fig/fig_68_0.png)

___

### References

* [Deep Graph Library](https://www.dgl.ai/)
* [graph-tool](https://graph-tool.skewed.de/)
* [igraph](https://igraph.org/python/)
* [Leiden](https://leidenalg.readthedocs.io)
* [NetworKit]()
* [NetworkX](https://networkx.github.io)
* [Pandas](https://pandas.pydata.org/)
* [PyTorch Geometric](https://pytorch-geometric.readthedocs.io)
