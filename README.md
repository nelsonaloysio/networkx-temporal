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

A Jupyter notebook with the following code is also available at [notebook.ipynb](notebook.ipynb).

### Build temporal graph

The `Temporal{Di,Multi,MultiDi}Graph` class uses NetworkX graphs internally to allow easy manipulation of its data structures:

```python
import networkx_temporal as nxt

TG = nxt.TemporalDiGraph(t=4)

TG[0].add_edge("a", "b")
TG[1].add_edge("c", "b")
TG[2].add_edge("c", "b")
TG[2].add_edge("d", "c")
TG[2].add_edge("d", "e")
TG[3].add_edge("f", "e")
TG[3].add_edge("f", "a")
TG[3].add_edge("f", "b")

print(f"t = {len(TG)} time steps\n"
      f"V = {TG.order()} nodes ({TG.temporal_order()} unique, {TG.total_order()} total)\n"
      f"E = {TG.size()} edges ({TG.temporal_size()} unique, {TG.total_size()} total)")

# t = 4 time steps
# V = [2, 2, 4, 4] nodes (6 unique, 12 total)
# E = [1, 1, 3, 3] edges (7 unique, 8 total)
```

### Draw snapshots

```python
import matplotlib.pyplot as plt

draw_opts = {"arrows": True,
             "node_color": "#aaa",
             "node_size": 250,
             "with_labels": True}

fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(8, 2), constrained_layout=True)

for t, G in enumerate(TG):
    nx.draw(G, pos=nx.kamada_kawai_layout(G), ax=ax[t], **draw_opts)
    ax[t].set_title(f"$t$ = {t}")

plt.show()
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/fig/graph_snapshots.png)

### Slice into time bins

Once initialized, a specified number of bins can be returned in a new object of the same type using `slice`:

```python
TGS = TG.slice(bins=2)
TGS.nodes()

# [NodeView(('a', 'b', 'c')), NodeView(('a', 'b', 'c', 'd', 'e', 'f'))]
```

By default, created bins are composed of non-overlapping edges and might have uneven size. To balance them, pass `qcut=True`:

```python
TGS = TG.slice(bins=2, qcut=True)
TGS.nodes()

# [NodeView(('a', 'b', 'c', 'd', 'e')), NodeView(('a', 'b', 'e', 'f'))]
```

Note that in some cases, the `qcut` method may not be able to split the graph into the number of bins requested and will return the maximum number of bins possible.

Additionally, either `duplicates=True` (allows duplicate edges among bins) or `rank_first=True` (ranks edges in order of appearance) may be used to avoid exceptions.

___

### Convert from static graph

Static graphs can carry temporal information either in the node- or edge-level attributes.

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
    ("c", "b", {"t": 2}),
    ("f", "e", {"t": 3}),
    ("f", "a", {"t": 3}),
    ("f", "b", {"t": 3}),
])

print(G)

# MultiDiGraph with 6 nodes and 8 edges
```

#### Node-level time attribute

Converting a static graph with node-level temporal data to a temporal graph object (`node_level` considers the source node's time by default when slicing edges):

```python
TG = nxt.from_static(G, attr="t", attr_level="node", node_level="source", bins=None, qcut=None)
TG.edges(data=True)

# [OutMultiEdgeDataView([('a', 'b', {'t': 0})]),
#  OutMultiEdgeDataView([('c', 'b', {'t': 1}), ('c', 'b', {'t': 2})]),
#  OutMultiEdgeDataView([('d', 'c', {'t': 2}), ('d', 'e', {'t': 2})]),
#  OutMultiEdgeDataView([('f', 'e', {'t': 3}), ('f', 'a', {'t': 3}), ('f', 'b', {'t': 3})])]
```

Note that considering node-level attributes resulted in misplacing the edge `(c, b, 2)` in the conversion from static to temporal, as it is duplicated at times 1 and 2.

#### Edge-level time attribute

Converting a static graph with edge-level temporal data to a temporal graph object (edge's time applies to both source and target nodes):

```python
TG = nxt.from_static(G, attr="t", attr_level="edge", bins=None, qcut=None)
TG.edges(data=True)

# [OutMultiEdgeDataView([('a', 'b', {'t': 0})]),
#  OutMultiEdgeDataView([('c', 'b', {'t': 1})]),
#  OutMultiEdgeDataView([('c', 'b', {'t': 2}), ('d', 'c', {'t': 2}), ('d', 'e', {'t': 2})]),
#  OutMultiEdgeDataView([('f', 'e', {'t': 3}), ('f', 'a', {'t': 3}), ('f', 'b', {'t': 3})])]
```

Both methods result in the same number of edges, but a higher number of nodes, as they appear in more than one bin in order to preserve all edges in the static graph.

___

## Transform temporal graph

Once a temporal graph is instantiated, some methods are implemented that allow returning snaphots, events or unified temporal graphs.

### Get snapshots

Returns a list of graphs internally stored under `_data` in the temporal graph object, also accessible by iterating through the object:

```python
STG = TG.to_snapshots()
STG

# [<networkx.classes.multidigraph.MultiDiGraph at 0x7fa0ac6faf50>,
#  <networkx.classes.multidigraph.MultiDiGraph at 0x7fa0ac72aa90>,
#  <networkx.classes.multidigraph.MultiDiGraph at 0x7fa0ac725c10>,
#  <networkx.classes.multidigraph.MultiDiGraph at 0x7fa0ac726290>]
```

```python
TG.to_snapshots() == TG._data

# True
```

### Get static graph

Builds a static or flattened graph containing all the edges found at each time step.

```python
G = TG.to_static()
fig = plt.figure(figsize=(2, 2))
nx.draw(G, pos=nx.kamada_kawai_layout(G), **draw_opts)
plt.show()
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/fig/graph_static.png)

Note that the above graph is a `MultiGraph`, but the visualization is a simple graph drawing a single edge among each node pair.

### Get sequence of events

An event-based temporal graph (ETG) is a sequence of 3- or 4-tuple edge-based events.

* 3-tuples: `(u, v, t)`, where elements are the source node, target node, and time step of the observed event (also known as a stream graph);

* 4-tuples: `(u, v, t, e)`, where `e` is either a positive (1) or negative (-1) unity for edge addition and deletion, respectively.

```python
ETG = TG.to_events()  # stream=True (default)
ETG

# [('a', 'b', 0),
#  ('c', 'b', 1),
#  ('c', 'b', 2),
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
#  ('d', 'c', 2, 1),
#  ('d', 'e', 2, 1),
#  ('f', 'e', 3, 1),
#  ('f', 'a', 3, 1),
#  ('f', 'b', 3, 1),
#  ('c', 'b', 3, -1),
#  ('d', 'c', 3, -1),
#  ('d', 'e', 3, -1)]
```

### Get unified temporal graph

The unified temporal graph (UTG) is a single graph that contains the original data plus proxy nodes and edge couplings connecting sequential temporal nodes.

```python
UTG = TG.to_unified(add_couplings=True,
                    add_proxy_nodes=False,
                    proxy_nodes_with_attr=True,
                    prune_proxy_nodes=True)
print(UTG)

# DiGraph with 12 nodes and 14 edges
```

```python
nodes = sorted(TG.temporal_nodes())
pos = {
    node: (nodes.index(node.rsplit("_")[0]), -int(node.rsplit("_")[1]))
    for node in UTG.nodes()
}
fig = plt.figure(figsize=(4, 4))
nx.draw(UTG, pos=pos, connectionstyle="arc3,rad=0.25", **draw_opts)
plt.show()
```

![png](https://github.com/nelsonaloysio/networkx-temporal/raw/main/fig/graph_unified.png)

### Convert back to TemporalGraph object

Functions to convert a newly created STG, ETG, or UTG back to a temporal graph object are also implemented.

```python
nxt.from_snapshots(STG)
nxt.from_events(ETG, directed=True, multigraph=False)
nxt.from_unified(UTG)
```

___

## Get temporal information

All methods implemented by `networkx`, e.g., `{in_,out_}degree`, are also available to be executed sequentially on the stored time slices.

A few additional methods that consider all time slices are also implemented for convenience, e.g., `temporal_{in_,out_}degree`.

### Node degrees

```python
TG.degree()

# [DiMultiDegreeView({'b': 1, 'a': 1}),
#  DiMultiDegreeView({'c': 1, 'b': 1}),
#  DiMultiDegreeView({'b': 1, 'c': 2, 'd': 2, 'e': 1}),
#  DiMultiDegreeView({'a': 1, 'b': 1, 'e': 1, 'f': 3})]
```

To obtain the degrees of nodes at a specific time step, use the `degree` method with the temporal graph index:

```python
TG[0].degree()

# DiMultiDegreeView({'b': 1, 'a': 1})
```

And to obtain the degree of all nodes or a specific node considering all time steps:

```python
TG.temporal_degree()

# {'c': 3, 'a': 2, 'f': 3, 'd': 2, 'b': 4, 'e': 2}
```

```python
TG.temporal_degree("a")

# 2
```

### Node neighborhoods

```python
TG.neighbors("c")

# [[], ['b'], ['b'], []]
```

To obtain the temporal neighborhood of a node considering all time steps, use the method `temporal_neighbors`:

```python
TG.temporal_neighbors("c")

# ['b']
```

### Order and size

```python
TG.order(), TG.size()

# ([2, 2, 4, 4], [1, 1, 3, 3])
```

Note that the temporal order and size are defined as the number of unique nodes and edges, respectively, across all time steps:

```python
TG.temporal_order(), TG.temporal_size()

# (6, 7)
```

To consider nodes or edges with distinct attributes as non-unique, pass `data=True`:

```python
TG.temporal_order(data=True), TG.temporal_size(data=True)

# (6, 8)
```

And to obtain the total number of nodes and edges across all time steps, use the `total_order` and `total_size` methods instead:

```python
TG.total_order(), TG.total_size()  # sum(TG.order()), sum(TG.size())

# (12, 8)
```

___

### References

* [NetworkX](https://networkx.github.io)
* [Pandas](https://pandas.pydata.org/)
