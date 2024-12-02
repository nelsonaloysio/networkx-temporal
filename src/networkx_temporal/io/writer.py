import os
import os.path as osp
import zipfile
from io import BufferedWriter, BytesIO, StringIO, TextIOWrapper
from typing import Callable, Optional, Union

import networkx as nx

from .io import _get_filepath, _get_filename, _get_format, _get_format_ext, _get_function
from ..typing import Literal, StaticGraph, TemporalGraph
from ..utils import is_static_graph, is_temporal_graph

DEFAULT_FORMAT = "graphml"

COMPRESSION = Literal[
    "ZIP_STORED",
    "ZIP_DEFLATED",
    "ZIP_BZIP2",
    "ZIP_LZMA",
]


def write_graph(
    TG: Union[TemporalGraph, StaticGraph],
    file: Optional[Union[str, BufferedWriter, BytesIO]] = None,
    frmt: Optional[Union[str, Callable]] = None,
    makedirs: bool = False,
    compression: Optional[COMPRESSION] = None,
    compresslevel: Optional[int] = None,
    allowZip64: bool = False,
    **kwargs
) -> Union[bytes, None]:
    """
    Writes a :class:`~networkx_temporal.graph.TemporalGraph` to a compressed
    `ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile>`__.

    If the object contains more than one snapshot, such as after calling
    :func:`~networkx_temporal.graph.TemporalGraph.slice`, this function writes a single ZIP archive,
    in which each file refers to a snapshot. Graph files are saved as ``{name}_{t}.{ext}``,
    where ``t`` is their snapshot index and ``ext`` is their extension format.

    .. rubric:: Example

    Writing a temporal graph to a compressed ZIP file:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.TemporalGraph()
        >>> tx.write_graph(TG, "snapshots.graphml.zip")

    .. seealso::

        The latest `read and write documentation
        <https://networkx.org/documentation/stable/reference/readwrite/index.html>`__
        from NetworkX for a list of supported formats.

    :param TG: :class:`~networkx_temporal.graph.TemporalGraph` to write.
    :param object file: Binary file-like object or string containing path to ZIP file. Optional. If
        ``None`` (default), returns content as bytes.
    :param frmt: Extension format or callable function to write graphs with. If unset and ``file``
        is a string, it is inferred from it. Otherwise, defaults to ``'graphml'``.
    :param makedirs: Whether to create directories to file if they do not exist.
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
    path = _get_filepath(file)
    name = _get_filename(path)
    frmt = _get_format(path, frmt)
    func = _get_function(frmt, "write")

    if frmt is None:
        frmt, func = DEFAULT_FORMAT, getattr(nx, f"write_{DEFAULT_FORMAT}")

    assert type(file) != str or not osp.isdir(file),\
        "Argument `file` must be a file path or object, not a directory."
    assert type(file) != TextIOWrapper,\
        f"File must be opened in binary mode, received {type(file)} but expected {BufferedWriter}."
    assert type(file) != StringIO,\
        f"Buffer must be binary, received {type(file)} but expected {BytesIO}."
    assert frmt is not None,\
        "Missing extension format to write graph in file name or `frmt` parameter."
    assert type(frmt) == str or callable(frmt),\
        f"Argument `frmt` must be a string or callable function, received: {type(frmt)}."
    assert func is not None,\
        f"Extension '{frmt}' is not supported by NetworkX. Supported formats: "\
        f"{[f.split('write_', 1)[-1] for f in dir(nx) if f.startswith('write_')]}."
    assert compression is None or compression.upper() in COMPRESSION.__args__,\
        f"Argument `compression` must be among {COMPRESSION.__args__}."

    if is_static_graph(TG):
        TG = [TG]  # Allows a single graph to be passed as input.

    if makedirs and name is not None:
        os.makedirs(osp.dirname(file), exist_ok=True)

    compression = getattr(zipfile, (compression or "ZIP_STORED").upper())
    file, nofile = (BytesIO(), True) if file is None else (file, False)
    name = osp.basename((TG.name if is_temporal_graph(TG) else None) or name or 'snapshot')
    ext = _get_format_ext(frmt)

    with zipfile.ZipFile(file, "w",
                         compression=compression,
                         compresslevel=compresslevel,
                         allowZip64=allowZip64) as zf:

        for t, G in enumerate(TG):
            filename = f"{name}{f'_{t}' if len(TG) > 1 else ''}{ext}"

            with BytesIO() as buffer:
                func(G, buffer, **kwargs)
                zf.writestr(filename, buffer.getvalue())

    if type(file) == BytesIO:
        file.seek(0)

    return file.read() if nofile else None
