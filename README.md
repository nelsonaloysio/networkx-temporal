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

## Usage

Examples of usage below are also available as an interactive [Jupyter notebook](https://github.com/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal-example.ipynb) ([open on **Colab**](https://colab.research.google.com/github/nelsonaloysio/networkx-temporal/blob/main/notebook/networkx-temporal-example.ipynb)).

## Basics

### Build temporal graph

The `TemporalGraph` class extends NetworkX to temporal graphs, allowing easy manipulation of its internal data structure:

```python
>>> TG = tx.TemporalGraph(t=4, directed=True, multigraph=False)
>>>
>>> TG[0].add_edge("a", "b")
>>> TG[1].add_edge("c", "b")
>>> TG[2].add_edge("d", "c")
>>> TG[2].add_edge("d", "e")
>>> TG[2].add_edge("a", "c")
>>> TG[3].add_edge("f", "e")
>>> TG[3].add_edge("f", "a")
>>> TG[3].add_edge("f", "b")
>>>
>>> print(TG)
```

```none
TemporalDiGraph (t=4) with 12 nodes and 8 edges
```

```python
>>> print(f"t = {len(TG)} time steps\n"
>>>       f"V = {TG.order()} nodes ({TG.temporal_order()} unique, {TG.total_nodes()} total)\n"
>>>       f"E = {TG.size()} edges ({TG.temporal_size()} unique, {TG.total_edges()} total)")
```

```none
t = 4 time steps
V = [2, 2, 4, 4] nodes (6 unique, 12 total)
E = [1, 1, 3, 3] edges (8 unique, 8 total)
```

```python
>>> draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_7.png)

### Slice into temporal bins

Once initialized, a specified number of bins can be returned in a new object of the same type using `slice`:

```python
>>> TG = TG.slice(bins=2)
>>> draw_temporal_graph(TG, figsize=(4, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_9.png)

By default, created bins are composed of non-overlapping edges and might have uneven order and size.

To balance them, pass `qcut=True`:

```python
>>> TG = TG.slice(bins=2, qcut=True)
>>> draw_temporal_graph(TG, figsize=(4, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_11.png)

> Note that in some cases it may not be able to split the graph into the number of bins requested, returning the maximum possible number instead.
> Forcing a number of bins can be achieved by setting `rank_first=True` to balance snapshots considering the order of appearence of nodes or edges.

### Convert to directed or undirected

We can easily convert the edge directions by calling the same methods available from `networkx`:

```python
>>> TG.to_undirected()
```

```none
TemporalGraph (t=4) with 12 nodes and 8 edges
```

```python
>>> TG.to_directed()
```

```none
TemporalDiGraph (t=4) with 12 nodes and 16 edges
```

___

## Common metrics

All methods implemented by `networkx`, e.g., `degree`, are also available to be executed sequentially on the stored time slices.

A few additional methods that consider all time slices are also implemented for convenience, e.g., `temporal_degree` and `temporal_neighbors`.

### Degree centrality

```python
>>> TG.degree()
>>> # TG.in_degree()
>>> # TG.out_degree()
```

```none
[DiDegreeView({'a': 2, 'b': 2}),
 DiDegreeView({'c': 2, 'b': 2}),
 DiDegreeView({'d': 4, 'c': 4, 'e': 2, 'a': 2}),
 DiDegreeView({'f': 6, 'e': 2, 'a': 2, 'b': 2})]
```

```python
>>> TG.temporal_degree()
>>> # TG.temporal_in_degree()
>>> # TG.temporal_out_degree()
```

```none
{'e': 4, 'b': 6, 'f': 6, 'a': 6, 'd': 4, 'c': 6}
```

Or to obtain the degree of a specific node:

```python
>>> TG[0].degree("a")
>>> # TG[0].in_degree("a")
>>> # TG[0].out_degree("a")
```

```none
2
```

```python
>>> TG.temporal_degree("a")
>>> # TG.temporal_in_degree("a")
>>> # TG.temporal_out_degree("a")
```

```none
6
```

### Node neighborhoods

```python
>>> TG.neighbors("c")
```

```none
[[], ['b'], ['d', 'a'], []]
```

To obtain the neighborhood of a node considering all time steps, use the method `temporal_neighbors`:

```python
>>> TG.temporal_neighbors("c")
```

```none
{'a', 'b', 'd'}
```

### Order and size

To get the number of nodes and edges in each step:

```python
>>> print("Order:", TG.order())
>>> print("Size:", TG.size())
```

```none
Order: [2, 2, 4, 4]
Size: [2, 2, 6, 6]
```

#### Temporal order and size

The temporal order and size are respectively defined as the length of `TG.temporal_nodes()`, i.e., unique nodes in all time steps, and the length of `TG.temporal_size()`, i.e., sum of edges or interactions across all time steps.

```python
>>> print("Temporal nodes:", TG.temporal_order())
>>> print("Temporal edges:", TG.temporal_size())
```

```none
Temporal nodes: 6
Temporal edges: 16
```

#### Total number of nodes and edges

To get the actual number of nodes and edges across all time steps:

> Note that the temporal size of a graph will always be equal to its total number of edges, i.e., `TG.temporal_size() == TG.total_edges()`.

```python
>>> print("Total nodes:", TG.total_nodes())  # TG.total_nodes() != TG.temporal_order()
>>> print("Total edges:", TG.total_edges())  # TG.total_edges() == TG.temporal_size()
```

```none
Total nodes: 12
Total edges: 16
```

___

## Convert from static to temporal graph

Static graphs can carry temporal information in either the node- or edge-level attributes.

Slicing a graph into bins usually result in the same number of edges, but a higher number of nodes, as they may appear in more than one snapshot.

In the example below, we create a static multigraph in which both nodes and edges are attributed with the time step `t` in which they are observed:

```python
>>> G = nx.MultiDiGraph()
>>>
>>> G.add_nodes_from([
>>>     ("a", {"time": 0}),
>>>     ("b", {"time": 0}),
>>>     ("c", {"time": 1}),
>>>     ("d", {"time": 2}),
>>>     ("e", {"time": 3}),
>>>     ("f", {"time": 3}),
>>> ])
>>>
>>> G.add_edges_from([
>>>     ("a", "b", {"time": 0}),
>>>     ("c", "b", {"time": 1}),
>>>     ("d", "c", {"time": 2}),
>>>     ("d", "e", {"time": 2}),
>>>     ("a", "c", {"time": 2}),
>>>     ("f", "e", {"time": 3}),
>>>     ("f", "a", {"time": 3}),
>>>     ("f", "b", {"time": 3}),
>>> ])
>>>
>>> print(G)
```

```none
MultiDiGraph with 6 nodes and 8 edges
```

### Node-level time attributes

Converting a static graph with node-level temporal data to a temporal graph object (`node_level` considers the source node's time by default when slicing edges):

```python
>>> TG = tx.from_static(G).slice(attr="time", attr_level="node", node_level="source", bins=None, qcut=None)
>>> draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_35.png)

Note that considering node-level attributes resulted in placing the edge `(a, c, 2)` in $t=0$ instead, as the source node `a` attribute is set to `t=0`:

```python
>>> G.nodes(data="time")["a"]
```

```none
0
```

### Edge-level time attributes

Converting a static graph with edge-level temporal data to a temporal graph object (edge's time applies to both source and target nodes):

```python
>>> TG = tx.from_static(G).slice(attr="time", attr_level="edge", bins=None, qcut=None)
>>> draw_temporal_graph(TG, figsize=(8, 2))
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_39.png)

In this case, considering edge-level attributes results in placing the edge `(a, c, 2)` in $t=2$, as expected.

___

## Transform temporal graph

Once a temporal graph is instantiated, the following methods allow returning static graphs, snapshots, events or unified representations.

Due to the way the underlying data is represented, some of these objects (i.e., those with unique nodes) do not allow dynamic node attributes.

> Note that the total number of nodes $V$ and edges $E$ of the returned object might differ from the number of temporal nodes $V_T$ and edges $E_T$.

| Method | Order | Size | Dynamic node attributes | Dynamic edge attributes |
| --- | :---: | :---: | :---: | :---: |
| `to_static` | $V = V_T$ | $E = E_T$ | ❌ | ✅ |
| `to_snapshots` | $V \ge V_T$ | $E = E_T$ | ✅ | ✅ |
| `to_events` | $V = V_T$ | $E = E_T$ | ❌ | ❌ |
| `to_unified` | $V \ge V_T$ | $E \ge E_T$ | ✅ | ✅ |

### Convert to different object type

Temporal graphs may be converted to a different object type by calling `convert` or passing `to={parameter}` to the above methods.

| Format | Parameter (Package) | Parameter (Alias) |
| --- | :---: | :---: |
| [Deep Graph Library](https://www.dgl.ai/) | `dgl` | -
| [graph-tool](https://graph-tool.skewed.de/) | `graph_tool` | `gt`
| [igraph](https://igraph.org/python/) | `igraph` | `ig`
| [NetworKit](https://networkit.github.io/) | `networkit` | `nk`
| [PyTorch Geometric](https://pytorch-geometric.readthedocs.io) | `torch_geometric` | `pyg`
| [Teneto](https://teneto.readthedocs.io) | `teneto` | -

```python
>>> tx.convert(G, "igraph")
```

```none
<igraph.Graph at 0x7fc242f76050>
```

### Static graph

Builds a static or flattened graph containing all the edges found at each time step:

```python
>>> G = TG.to_static()
>>> draw_temporal_graph(G, suptitle="Static Graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_44.png)

### Snapshot-based temporal graph

The snapshot-based temporal graph (STG) is a list of graphs directly accessible under `data` in the temporal graph object:

```python
>>> STG = TG.to_snapshots()
```

### Event-based temporal graph

An event-based temporal graph (ETG) is a sequence of 3- or 4-tuple edge-based events.

* 3-tuples ($u, v, t$), where elements are the source node, target node, and time step of the observed event (also known as a stream graph);

* 4-tuples ($u, v, t, \epsilon$), where $\epsilon$ is either a positive (1) or negative (-1) unity representing edge addition and deletion events, respectively.

Depending on the temporal graph data, one of these may allow a more compact representation than the other.

```python
>>> ETG = TG.to_events()  # stream=True (default)
>>> ETG
```

```none
[('a', 'b', 0),
 ('c', 'b', 1),
 ('a', 'c', 2),
 ('d', 'c', 2),
 ('d', 'e', 2),
 ('f', 'e', 3),
 ('f', 'a', 3),
 ('f', 'b', 3)]
```

```python
>>> ETG = TG.to_events(stream=False)
>>> ETG
```

```none
[('a', 'b', 0, 1),
 ('c', 'b', 1, 1),
 ('a', 'b', 1, -1),
 ('a', 'c', 2, 1),
 ('d', 'c', 2, 1),
 ('d', 'e', 2, 1),
 ('c', 'b', 2, -1),
 ('f', 'e', 3, 1),
 ('f', 'a', 3, 1),
 ('f', 'b', 3, 1),
 ('a', 'c', 3, -1),
 ('d', 'c', 3, -1),
 ('d', 'e', 3, -1)]
```

### Unified temporal graph

The unified temporal graph (UTG) is a single graph that contains the original data plus proxy nodes and edge couplings connecting sequential temporal nodes.

```python
>>> UTG = TG.to_unified(add_couplings=True)
>>> print(UTG)
```

```none
MultiDiGraph named 'UTG (t=4, proxy_nodes=6, edge_couplings=2)' with 12 nodes and 14 edges
```

```python
>>> nodes = sorted(TG.temporal_nodes())
>>> pos = {node: (nodes.index(node.rsplit("_")[0]), -int(node.rsplit("_")[1])) for node in UTG.nodes()}
>>> draw_temporal_graph(UTG, pos=pos, figsize=(4, 4), connectionstyle="arc3,rad=0.25", suptitle="Unified Temporal Graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_52.png)

### Convert back to TemporalGraph object

Functions to convert a newly created STG, ETG, or UTG back to a temporal graph object are also implemented.

```python
>>> tx.from_snapshots(STG)
```

```none
TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges
```

```python
>>> tx.from_events(ETG, directed=True, multigraph=True)
```

```none
TemporalDiGraph (t=4) with 12 nodes and 8 edges
```

```python
>>> tx.from_unified(UTG)
```

```none
TemporalMultiDiGraph (t=4) with 12 nodes and 8 edges
```

___

## Community detection

As a toy example, let's first use a [Stochastic Block Model](https://networkx.org/documentation/stable/reference/generated/networkx.generators.community.stochastic_block_model.html) to generate 4 snapshots, in which each of the 5 clusters of 5 nodes each continuously mix together:

```python
>>> snapshots = 4   # Temporal graphs to generate.
>>> clusters = 5    # Number of clusters/communities.
>>> order = 5       # Nodes in each cluster.
>>> intra = .9      # High initial probability of intra-community edges.
>>> inter = .1      # Low initial probability of inter-community edges.
>>> change = .125   # Change in intra- and inter-community edges over time.
>>>
>>> # Get probability matrix for each snapshot.
>>> probs = [[[
>>>     (intra if i == j else inter) + (t * change * (-1 if i == j else 1))
>>>     for j in range(clusters)]
>>>     for i in range(clusters)]
>>>     for t in range(snapshots)]
>>>
>>> # Create graphs from probabilities.
>>> graphs = {}
>>> for t in range(snapshots):
>>>     graphs[t] = nx.stochastic_block_model(clusters*[order], probs[t], seed=10)
>>>     graphs[t].name = t
>>>
>>> # Create temporal graph from snapshots.
>>> TG = tx.from_snapshots(graphs)
```

Let's plot the temporal graph snapshots, with colors representing the ground truths and highlighting intra-community edges.

```python
>>> import matplotlib.pyplot as plt
>>>
>>> def get_edge_color(edges: list, node_color: dict):
>>>     return [node_color[u] if node_color[u] == node_color[v] else "#00000035" for u, v in edges]
>>>
>>> c = plt.cm.tab10.colors
>>>
>>> # Node positions.
>>> pos = nx.circular_layout(TG.to_static())
>>>
>>> # Community ground truths.
>>> node_color = [c[i // clusters] for i in range(TG.temporal_order())]
>>>
>>> # Colorize intra-community edges.
>>> temporal_opts = {t: {"edge_color": get_edge_color(TG[t].edges(), node_color)} for t in range(len(TG))}
>>>
>>> # Plot snapshots with community ground truths.
>>> draw_temporal_graph(
>>>     TG,
>>>     pos=pos,
>>>     figsize=(14, 4),
>>>     node_color=node_color,
>>>     temporal_opts=temporal_opts,
>>>     connectionstyle="arc3,rad=0.1",
>>>     suptitle="Ground truth")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_60.png)

### Modularity: on static graph

The [leidenalg](https://leidenalg.readthedocs.io) package implements optimization algorithms for community detection that may be applied on snapshot-based temporal graphs.

Such algorithms may help with descriptive or exploratory tasks and post-hoc network analysis, although they lack statistical rigor for inference purposes.

For example, depending on the initial node community assigments (e.g., with `seed=0` below), [modularity](https://leidenalg.readthedocs.io/en/stable/reference.html#modularityvertexpartition) fails to retrieve the true communities:

```python
>>> import leidenalg as la
>>>
>>> membership = la.find_partition(
>>>     TG.to_static("igraph"),
>>>     la.ModularityVertexPartition,
>>>     n_iterations=-1,
>>>     seed=0,
>>> )
>>>
>>> node_color = [c[m] for m in membership.membership]
>>> edge_color = get_edge_color(TG.to_static().edges(), node_color)
>>>
>>> draw_temporal_graph(
>>>     TG.to_static(),
>>>     pos=pos,
>>>     figsize=(4, 4),
>>>     node_color=node_color,
>>>     edge_color=edge_color,
>>>     connectionstyle="arc3,rad=0.1",
>>>     suptitle="Communities found by modularity on static graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_62.png)

### Modularity: on each snapshot

Running the same algorithm separately on each of the generated snapshots retrieves the correct clusters only on the first ($t=0$).

In addition, community indices/colors along snapshots are not fixed, which makes understanding their mesoscale dynamics harder.

```python
>>> temporal_opts = {}
>>>
>>> for t in range(len(TG)):
>>>     membership = la.find_partition(
>>>         TG[t:t+1].to_static("igraph"),
>>>         la.ModularityVertexPartition,
>>>         n_iterations=-1,
>>>         seed=0,
>>>     )
>>>     node_color = [c[m] for m in membership.membership]
>>>     edge_color = get_edge_color(TG[t].edges(), node_color)
>>>     temporal_opts[t] = {"node_color": node_color, "edge_color": edge_color}
>>>
>>> draw_temporal_graph(
>>>     TG,
>>>     pos=pos,
>>>     figsize=(14, 4),
>>>     temporal_opts=temporal_opts,
>>>     connectionstyle="arc3,rad=0.1",
>>>     suptitle="Communities found by modularity on snapshots")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_64.png)

### Modularity: on temporal graph

[Coupling temporal nodes](https://leidenalg.readthedocs.io/en/stable/multiplex.html#slices-to-layers) allows the same algorithm to correctly retrieve the ground truths in this case, and maintain community indices/colors fixed.

> Note that the `interslice_weight` among temporal nodes in a sequence of snapshots defaults to `1.0`, but may be adjusted accordingly.

```python
>>> temporal_opts = {}
>>>
>>> temporal_membership, improvement = la.find_partition_temporal(
>>>     TG.to_snapshots("igraph"),
>>>     la.ModularityVertexPartition,
>>>     interslice_weight=1.0,
>>>     n_iterations=-1,
>>>     seed=0,
>>>     vertex_id_attr="_nx_name"
>>> )
>>>
>>> for t in range(len(TG)):
>>>     node_color = [c[m] for m in membership.membership]
>>>     edge_color = get_edge_color(TG[t].edges(), node_color)
>>>     temporal_opts[t] = {"node_color": node_color, "edge_color": edge_color}
>>>
>>> draw_temporal_graph(
>>>     TG,
>>>     figsize=(14, 4),
>>>     pos=pos,
>>>     temporal_opts=temporal_opts,
>>>     connectionstyle="arc3,rad=0.1",
>>>     suptitle="Communities found by modularity on temporal graph")
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/docs/figures/fig_66.png)

___

## References

* [Deep Graph Library](https://www.dgl.ai/)
* [graph-tool](https://graph-tool.skewed.de/)
* [igraph](https://igraph.org/python/)
* [Leiden](https://leidenalg.readthedocs.io)
* [NetworKit](https://networkit.github.io/)
* [NetworkX](https://networkx.github.io)
* [Pandas](https://pandas.pydata.org/)
* [PyTorch Geometric](https://pytorch-geometric.readthedocs.io)
* [Teneto](https://teneto.readthedocs.io)
