from typing import Optional, Union

import networkx as nx

from ..convert import convert, FORMATS


def from_snapshots(graphs: Union[dict, list]) -> list:
    """
    Returns temporal graph from sequence of snapshots.

    :param graphs: List or dictionary of NetworkX graphs
    """
    T = list(graphs.keys()) if type(graphs) == dict else range(len(graphs))

    directed = graphs[T[0]].is_directed()
    multigraph = graphs[T[0]].is_multigraph()

    assert type(graphs) in (dict, list),\
        "Argument `graphs` must be a list or dictionary of NetworkX graphs."

    assert len(graphs) > 0,\
        "Argument `graphs` must be a non-empty list or dictionary."

    assert all(type(graphs[t]) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph) for t in T),\
        "All elements in data must be valid NetworkX graphs."

    assert all(directed == graphs[T[t]].is_directed() for t in T),\
        "Mixed graphs and digraphs are not supported."

    assert all(multigraph == graphs[T[t]].is_multigraph() for t in T),\
        "Mixed graphs and multigraphs are not supported."

    from ..temporal import TemporalGraph
    TG = TemporalGraph(directed=directed, multigraph=multigraph, t=len(T))
    TG.data = graphs
    return TG


def to_snapshots(self, to: Optional[FORMATS] = None) -> list:
    """
    Returns a sequence of snapshots where each slice represent the state
    of the network at a given time, i.e., a list of NetworkX graphs.

    Internally, the temporal graph objeect already stores data as a list of
    graphs, so this method simply returns the object itself (`self._data`),
    optionally converting it to another format if specified in `to`.

    :param to: Format to convert the snapshots to (optional).
    """
    return [convert(G, to) for G in self] if to else self.data
