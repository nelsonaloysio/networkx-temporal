import os
import os.path as osp
import zipfile
from io import BufferedWriter, BytesIO, StringIO, TextIOWrapper
from typing import Callable, Optional, Union

import networkx as nx

from .readwrite import _get_filepath, _get_filename, _get_format, _get_format_ext, _get_function
from ..classes.types import is_static_graph, is_temporal_graph
from ..typing import Literal, StaticGraph, TemporalGraph

DEFAULT_COMPRESSION = "ZIP_STORED"
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
    format: Optional[Union[str, Callable]] = None,
    makedirs: bool = False,
    compression: Optional[COMPRESSION] = None,
    compresslevel: Optional[int] = None,
    allowZip64: bool = False,
    **kwargs
) -> Union[bytes, None]:
    """ Writes static or temporal graph to file or binary object.

    A compressed `ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile>`__
    is created in which each graph file refers to a snapshot. Graph files are saved as
    ``{name}_{t}.{ext}``, where ``t`` is their snapshot index and ``ext`` is the extension format.

    Note that a ``'.zip'`` extension is automatically added to the output file name if not present.

    .. rubric:: Example

    Writing a temporal graph to a compressed ZIP file:

    .. code-block:: python

        >>> import networkx_temporal as tx
        >>>
        >>> TG = tx.TemporalGraph()
        >>> tx.write_graph(TG, "snapshots.graphml.zip")

    .. seealso::

        The latest `read and write documentation
        <https://networkx.org/documentation/stable/reference/io/index.html>`__
        from NetworkX for a list of supported formats.

    :param object TG: A :class:`~networkx_temporal.classes.TemporalGraph` object.
    :param object file: Binary file-like object or string containing path to ZIP file. Optional. If
        ``None`` (default), returns content as bytes.
    :param format: Extension format or callable function to write graphs with. If unset and ``file``
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
    frmt = _get_format(path, format) or DEFAULT_FORMAT
    func = _get_function(frmt, "write")

    if type(file) == str and osp.isdir(file):
        raise TypeError("Argument `file` must be a file path or object, not a directory.")
    if type(file) == TextIOWrapper:
        raise TypeError(f"File must be opened in binary mode, received {type(file)} "
                        f"but expected {BufferedWriter}.")
    if type(file) == StringIO:
        raise TypeError(f"Buffer must be binary, received {type(file)} but expected {BytesIO}.")
    if frmt is None:
        raise RuntimeError("Format could not be determined from file name or `format` parameter.")
    if type(frmt) != str and not callable(frmt):
        raise TypeError(f"Argument `format` expects a string or callable, received: {type(frmt)}.")
    if compression is not None and compression.upper() not in COMPRESSION.__args__:
        raise ValueError(f"Argument `compression` must be among {COMPRESSION.__args__}.")
    if func is None:
        raise ValueError(f"Extension '{frmt}' is not supported by NetworkX. Supported formats: "
                         f"{[f[6:] for f in dir(nx) if f.startswith('write_')]}.")

    if is_static_graph(TG):
        TG = [TG]  # Allows a single graph to be passed as input.

    if makedirs and name is not None:
        os.makedirs(osp.dirname(file), exist_ok=True)
    if type(file) == str and not file.lower().endswith('.zip'):
        file += '.zip'

    compression = getattr(zipfile, (compression or DEFAULT_COMPRESSION).upper())
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
