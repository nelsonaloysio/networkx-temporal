# Changelog

<!--
## \[Version\] - YYYY-MM-DD
### Added
### Changed
### Deprecated
### Fixed
### Removed
-->

## \[1.4.3\] - Roadmap

### Added
- Alias `dynamic_sbm` to `dynamic_stochastic_block_model`.
- Argument `values` to `get_{edge,node}_attributes` returns a list or set of values per node/edge.

### Changed
- Argument `random_state` renamed to `seed` for `leiden_multislice_gpu` to match other functions.

### Deprecated
- Argument `sparse` from `{stochastic,dynamic_stochastic}_block_mdoel`.

## \[1.4.2\] - 07-08-2026

### Fixed
- For temporal multigraphs, `to_{,supra_}adjacency_matrix` matches (weighted) `to_{numpy,scipy}`.

## \[1.4.1\] - 07-08-2026

### Fixed
- Keyword argument filtering for CPU/GPU and static/temporal Leiden backends.

## \[1.4\] - 07-08-2026

### Added
- Arguments `node_attrs` and `edge_attrs` to `to_events` function to return node/edge attributes.
- Class method `get_edge_data` to iterate over temporal graph snapshots.
- Class methods `nodes` and `edges` with `copies` support, previously `temporal_{nodes,edges}`.
- Class property `timestamps` to get a list of edge timestamps based on current slicing.
- Community detection algorithms (Leiden and spectral clustering) for static and temporal graphs.
- Conversion functions `from_{cupy,numpy,pandas,spacy}` for static and temporal graphs.
- Conversion functions `to_{cugraph,cupy,pandas}` for static and temporal graphs.
- Function `isolates` to return a list of node isolates in each snapshot.
- Function `temporal_split` to split a temporal graph into train/val/test sets.
- Sparse temporal `to_supra_adjacency_matrix` function with CPU (SciPy) and GPU (CuPy) support.
- Loader `fediverse_graph` for temporal graph datasets from Fediverse. [networkx_temporal#4]
- Loader `travian_graph` for temporal graphs from the Travian dataset (attacks, messages, trades).
- Missing `supra` graph implementation for `to_numpy` conversion function.
- Support for GDF extension format from `networkx-gdf`.
- Support for node and edge attributes in `{from_to}_events` functions.
- Support for supra-adjacency matrix conversion in `to_{cupy,numpy,scipy}` functions.

### Changed
- All temporal graphs now start empty (`t=0`), with the first snapshot created on demand.
- Any new nodes and edges added to a temporal graph with zero snapshots create a new snapshot.
- Calling `pop` from a temporal graph with `index=None` raises `TypeError`.
- Functions `remove_{edges,nodes}_from` now support a list or list of lists of nodes/edges.
- Functions `subgraph` and `edge_subgraph` now return a TemporalGraph instead of a list of graphs.
- Functions `temporal_{node,edge}_matrix` renamed to `temporal_{node,edge}_similarity` for clarity.
- Item assignment is now permitted from object, not `graphs` attribute (e.g., `TG[0] = G`).
- Loader `from_snapshots` accepts snapshots from temporal graph objecs.
- Loader `read_graph` looks for compressed `.zip` extension if the provided file is not found.
- Passing `weight` to `temporal_size` or `edges` with `copies=False` raises `ValueError`.
- Review `slice` implementation. [networkx-temporal#3]
- SBM edge sampling from a Poisson distribution for multi/graphs, with Bernoulli as an option.
- Styling: variable `graph` used for time-agnostic implementations, `G` or `TG` otherwise.
- Utility functions `get_{edge,node}_attributes` skips nodes/edges without attributes by default.
- Utility functions refactored to `edges`, `nodes`, `time` submodules, now always require a graph.

### Deprecated
- Argument `apply_func` of `slice` deprecated in favor of `applymap`.
- Property `names` of `TemporalGraph` deprecated in favor of `index`.

### Fixed
- SBM edge sampling output matches sparse and dense matrix methods.

### Removed
- Argument `attr` from `to_events` function.


## \[1.3.3\] - 2027-07-01

### Added
- Added optional `mu` (mean) parameter for Gaussian degree vectors.

### Fixed
- Added missing `weight` argument to `size` and  `number_of_edges`.


## \[1.3.2\] - 2026-05-11

### Fixed
- Data loss calling `from_events` on event list with parallel edges if `multigraph=False`. [#5]


## \[1.3.1\] - 2026-04-14

### Changed
- Class method `add_snapshot` now returns graph object for variable assignment (empty by default).
- Parameter `delta` now explicitly stored as a graph attribute in `to_unrolled` graphs.
- Refactored `neighbors`, `all_neighbors` generators from functions and methods avoiding `reduce`.
- Refactored node and edge iteration from `temporal_{order,size}` and `degree_centrality`.

### Fixed
- Calling `temporal_{nodes,edges}` with `copies=False` and `data=True` raised `TypeError`.
- CollegeMsg and PubMed dataset files (nodes/edges) now included with PyPI package.
- Graph parameters (e.g., `name`) now preserved when converting from/to multigraphs.
- Import submodule `urllib.request` for external file downloading, not `urllib`.
- Parameter `index=False` for `get_{edge,node}_attributes` now considered for static graphs.


## \[1.3\] - 2025-11-26

### Added
- Drawing function `unrolled_layout`.
- Function `slice` argument `axis` in `[0, 1]` for time and node/edge bins.
- Improved NetworkX graph functions to `classes` module.
- Module `algorithms` with centrality, centralization, and community metrics.
- Module `generators` with example datasets and generative functions.
- Parameter `delta` added to `to_unrolled` (previously `to_unified`).
- Parameter `intervals` added to `slice` method of temporal graphs.
- Quality of life functions to temporal graph objects, for example, `from_multigraph`.
- Type objects `TemporalDiGraph`, `TemporalMultiGraph`, `TemporalMultiDiGraph`.
- Utility functions for static and temporal graphs.

### Changed
- Functions `transform.{from,to}_unrolled` renamed from `transform.{from,to}_unified`.
- Module `classes` renamed from `graph`.
- Module `readwrite` renamed from `io`.
- Parameter `copies` added to `order`, `number_of_nodes`, `size`, `number_of_edges` methods.
- Parameter `delta` renamed from `eps` (`transform.to_events`).
- Type object `TemporalGraph` now refers to undirected, non-multigraph temporal graphs.
- Wrapping methods of inherited NetworkX static graph classes by temporal graph classes.

### Deprecated
- Alias parameters for package conversion, for example, `'nk'` for `'networkit'`.

### Fixed
- Drawing node and edge elements returning empty plots with `labels=False`.
- Node-level slices on empty graphs (without edges) are now supported.
- Slicing a graph with `slice` when specifying `attr` but not `bins` now returns unique points.


## \[1.2.1\] - 2025-03-10

### Fixed
- Single graph drawing passing `fig` to `draw_networkx`.


## \[1.2\] - 2024-12-02

### Added
- Conversion functions from NetworkX to SNAP, StellarGraph.
- Function `is_static_graph` to `utils` module.
- Functions `to_{}` in `utils.convert` submodule.
- Method `convert` to temporal graph objects.
- Tests for order and size of `to_directed`, `to_undirected` output graphs.

### Changed
- Function `convert` moved to `utils.convert` submodule.
- Functions `is_frozen`, `is_temporal_graph` moved from `graph` to `utils` module.
- Package logo image.

### Fixed
- Copy missing `names` property to `{from,to}_multigraph` output graphs.
- Original object changed on `to_directed`, `to_undirected`.

### Removed
- Unused parameters from `temporal_neighbors`: `start` and `end`.


## \[1.1.1\] - 2024-11-22

### Fixed
- `typing` module compatibility with `python<3.11`.


## \[1.1\] - 2024-11-21

### Added
- Element-specific drawing with NetworkX: `draw_networkx_{nodes,edges,labels,edge_labels}`.
- Event-based representation with `to_events` using floats for interaction duration/interval.
- Function `is_frozen` to return single boolean value for temporal graph object.
- High-level `draw` function to support wrapping around possible multiple backends.
- Multigraph transform functions: `{from,to}_multigraph`.
- Override for `is_frozen` to return single boolean value for temporal graph.

### Changed
- Drawing defaults for node and edge colors using Matplotlib's `tab10` palette.
- Drawing parameter `layout` now accepts a callable to calculate node positions.
- Function `draw` refactored and renamed to `draw_networkx`.
- Module `drawing` renamed from `draw`.
- Module `utils` renamed from `convert`.
- Moved `tests` to repository root folder.
- Number of nodes when calling `str` on a temporal graph object do not consider node copies.
- Optimized `from_events` function to use ranges for edge addition/deletion (`1`/`-1`) events.
- Output of `from_events` is a (frozen) subgraph if `as_view=True` for reduced memory footprint.
- Output of `from_events` is a multigraph if parallel edges are not found and `multigraph=None`.
- Restructured package reference in documentation.

### Fixed
- Exception from rounded time values on `slice` resulting in duplicate categories.
- Exception in case a list of static graphs is passed as input to `write_graph`.
- Inconsistent `to_events` output in case of frozen graphs.
- Inconsistent `from_events` output in case of infinitely preserved edges.

### Removed
- Parameter from `to_events`: `stream` (replaced with `eps`).
- Parameters from `draw`: `fig_opts` and `temporal_opts` (replaced with `temporal_...`).


## \[1.0\] - 2024-09-26
- First release.
