# Changelog

<!--
## \[Version\] - YYYY-MM-DD
### Added
### Changed
### Deprecated
### Fixed
### Removed
-->

## \[1.3\] - 2025-09-17

### Added
- Functions `draw_unrolled` and `unrolled_layout` (`drawing` module).
- Module `algorithms` with node- and graph-level metrics.
- Module `generators` with
- Parameter `delta` added to `to_unrolled`.

### Changed
- Functions `transform.{from,to}_unrolled` renamed from `transform.{from,to}_unified`.
- Inheritance of NetworkX graph methods by temporal graph classes.
- Module `classes` renamed from `graph`.
- Module `readwrite` renamed from `io`.
- Parameter `delta` renamed from `eps` (`transform.to_events`).


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
- Element-specific drawing functions with NetworkX: `draw_networkx_{nodes,edges,labels,edge_labels}`.
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
- Optimized `from_events` function to use ranges to process edge addition/deletion (`1`/`-1`) events.
- Output of `from_events` is a (frozen) subgraph view if `as_view=True` for reduced memory footprint.
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
