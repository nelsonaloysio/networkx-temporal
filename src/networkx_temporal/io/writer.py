import os
import os.path as osp
import zipfile
from io import BytesIO
from typing import Optional

import networkx as nx

from ..typing import TemporalGraph, Literal

COMPRESSION = Literal[
    "ZIP_STORED",
    "ZIP_DEFLATED",
    "ZIP_BZIP2",
    "ZIP_LZMA",
]


def write_graph(
    TG: TemporalGraph,
    path: str,
    format: Optional[str] = None,
    makedirs: bool = False,
    compression: Optional[COMPRESSION] = None,
    compresslevel: Optional[int] = None,
    allowZip64: bool = False,
    **kwargs
) -> None:
    """
    Writes :class:`~networkx_temporal.TemporalGraph` to graph file or compressed
    `ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile>`__
    containing multiple snapshots.

    If the object contains more than one snapshot --- such as after calling
    :func:`~networkx_temporal.TemporalGraph.slice` --- this function writes a single ZIP archive,
    in which each file within refers to a snapshot. Files are named ``{name}_{t}.{format}``,
    where ``t`` is the snapshot index and ``format`` is the file extension.

    .. seealso::

        For a list of supported formats, see NetworkX's `read and write documentation
        <https://networkx.org/documentation/stable/reference/readwrite/index.html>`__.

    :param TG: :class:`~networkx_temporal.TemporalGraph` to write.
    :param path: Path to file. If it does not end with ''.zip'', it is automatically added as a suffix,
        if required. Example: ``'path/to/file.graphml.zip'``.
    :param str format: Extension format to use. Optional. If unset, it is inferred from ``path``.
        Must be among the supported formats by NetworkX.
    :param makedirs: Whether to create directories to path if they do not exist.
        Default is ``False``.
    :param str compression: Compression method to use. Optional. The following values are accepted:

        * ``'ZIP_STORED'``: no compression. This is the default.

        * ``'ZIP_DEFLATED'``: requires zlib.

        * ``'ZIP_BZIP2'``: requires bz2.

        * ``'ZIP_LZMA'``: requires lzma.

    :param compresslevel: Level of compression to use. Optional. Default is ``None``.
        The following values are accepted, depending on the compression method:

        * When using ``'ZIP_STORED'`` or ``'ZIP_LZMA'``, this keyword has no effect.

        * When using ``'ZIP_DEFLATED'``, integers ``0`` through ``9`` are accepted.

        * When using ``'ZIP_BZIP2'``, integers ``1`` through ``9`` are accepted.

    :param allowZip64: If ``True``, files with a ZIP64 extension will be created if
        needed. Otherwise, an exception will be raised when this would be necessary.
        Default is ``False``.
    :param kwargs: Additional arguments to pass to NetworkX writer function.
    """
    if path.endswith(".zip"):
        name, ext = osp.splitext(path[:-4]) if format is None else (path[:-4], format)
    else:
        name, ext = osp.splitext(path) if format is None else (path, format)

    ext = ext.lstrip(".")
    func = getattr(nx, f"write_{ext}", None)
    # func = getattr(nx, f"generate_{ext}", None)

    assert ext,\
        "Missing file extension to write graph, required if ``format`` is not set."

    assert func is not None,\
        f"Extension '{format}' is not supported by NetworkX. Supported formats: "\
        f"{[f.split('write_', 1)[-1] for f in dir(nx) if f.startswith('write_')]}."

    assert compression is None or compression.upper() in COMPRESSION.__args__,\
        f"Argument `compression` must be among {COMPRESSION.__args__}."

    compression = getattr(zipfile, (compression or "ZIP_STORED").upper())

    if makedirs:
        os.makedirs(osp.dirname(path), exist_ok=True)

    if type(TG) in (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph):
        TG = [TG]  # Allows a single graph to be passed as input.

    if len(TG) == 0:
        raise ValueError("TemporalGraph is empty.")

    if len(TG) == 1 and not path.endswith(".zip"):
        func(TG[0], path, **kwargs)
        return

    zipped = zipfile.ZipFile(path, "w",
                             compression=compression,
                             compresslevel=compresslevel,
                             allowZip64=allowZip64)

    with zipped as z:
        for t, G in enumerate(TG):
            filename = f"{osp.basename(name)}{f'_{t}' if len(TG) > 1 else ''}.{ext}"
            with BytesIO() as buffer:
                func(G, buffer, **kwargs)
                z.writestr(filename, buffer.getvalue())
