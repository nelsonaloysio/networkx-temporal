import os
import os.path as osp
import zipfile

import networkx as nx

from ..transform import from_snapshots, from_static
from ..typing import TemporalGraph


def read_graph(path: str, **kwargs) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.TemporalGraph` from graph file or compressed
    `ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile>`__
    containing multiple snapshots.

    Files within the compressed ZIP file must be named as ``{name}_{t}.{format}``,
    where ``t`` is the snapshot index and ``format`` is the file extension.
    See :func:`~networkx_temporal.write_graph` for more information.

    .. seealso::

        For a list of supported formats, see NetworkX's `read and write documentation
        <https://networkx.org/documentation/stable/reference/readwrite/index.html>`__.

    :param path: Path to file.
    :param kwargs: Additional arguments to pass to NetworkX reader function.

    :rtype: TemporalGraph
    """
    def load_graph(filename, f=None, **kwargs):
        ext = osp.splitext(filename)[-1]
        func = getattr(nx, f"read_{ext.lstrip('.')}", None)

        assert func is not None,\
            f"Extension '{ext}' is not supported by NetworkX. Supported formats: "\
            f"{[f.split('read_', 1)[-1] for f in dir(nx) if f.startswith('read_')]}."

        return func(f or filename, **kwargs)

    if not osp.isfile(path):
        raise FileNotFoundError(f"File '{path}' not found.")

    snapshots = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path, "r") as z:
            for filename in sorted(z.namelist()):
                with z.open(filename) as f:
                    G = load_graph(filename, f=f, **kwargs)
                    snapshots.append(G)
    else:
        G = load_graph(path, **kwargs)
        return from_static(G)

    return from_snapshots(snapshots)
