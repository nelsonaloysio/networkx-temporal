import os.path as osp
import zipfile
from io import BufferedReader, BytesIO, StringIO, TextIOWrapper
from typing import Callable, Optional, Union

import networkx as nx

from .utils import get_filepath, get_filename, get_format, get_function
from ..transform import from_snapshots, from_static
from ..typing import TemporalGraph


def read_graph(
    file: Union[str, BufferedReader, BytesIO],
    frmt: Optional[Union[str, Callable]] = None,
    **kwargs,
) -> TemporalGraph:
    """
    Returns :class:`~networkx_temporal.TemporalGraph` from graph file or compressed
    `ZipFile <https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile>`__
    containing multiple snapshots.

    Files within the compressed ZIP file must be named as ``{name}_{t}.{ext}``,
    where ``t`` is the snapshot index and ``ext`` is the extension format.
    See :func:`~networkx_temporal.write_graph` for more information.

    .. seealso::

        The `read and write documentation
        <https://networkx.org/documentation/stable/reference/readwrite/index.html>`__
        from NetworkX for a list of supported formats.

    :param object file: Binary file-like object or string containing path to ZIP file.
    :param frmt: Extension format or callable function to read compressed graphs with. If unset,
        it is inferred from each zipped file name.
    :param kwargs: Additional arguments to pass to NetworkX reader function.

    :rtype: TemporalGraph
    """
    def read(file, frmt, **kwargs):
        path = get_filepath(file)
        frmt = get_format(path, frmt)
        func = get_function(frmt, "read")

        assert frmt is not None,\
            "Missing extension format to read graph in file name or `frmt` parameter."
        assert type(frmt) == str or callable(frmt),\
            f"Argument `frmt` must be a string or callable function, received: {type(frmt)}."
        assert func is not None,\
            f"Extension '{frmt}' is not supported by NetworkX. Supported formats: "\
            f"{[f.split('read_', 1)[-1] for f in dir(nx) if f.startswith('read_')]}."

        return func(file, **kwargs)

    path = get_filepath(file)
    name = get_filename(path)

    assert type(file) != str or not osp.isdir(file),\
        "Argument `file` must be a file path or object, not a directory."
    assert type(file) != TextIOWrapper,\
        f"File must be opened in binary mode, received {type(file)} but expected {BufferedWriter}."
    assert type(file) != StringIO,\
        f"Buffer must be binary, received {type(file)} but expected {BytesIO}."

    if type(file) == bytes:
        file = BytesIO(file)

    if zipfile.is_zipfile(file):
        with zipfile.ZipFile(file, "r") as zf:
            assert len(zf.namelist()) > 0, "ZIP file is empty."

            if len(zf.namelist()) == 1:
                with zf.open(zf.namelist()[0]) as f:
                    TG = from_static(read(f, frmt, **kwargs))

            else:
                assert all(osp.splitext(z)[0].rsplit("_", 1)[-1].isdigit() for z in zf.namelist()),\
                    "Snapshots in ZIP file must contain an index 't', such as '{name}_{t}.{ext}'."

                TG = from_snapshots([
                    read(zf.open(z), frmt, **kwargs)
                    for z in sorted(zf.namelist(), key=lambda x: int(osp.splitext(x)[0].rsplit("_", 1)[-1]))
                ])

    else:
        TG = from_static(read(file, frmt, **kwargs))

    TG.name = name
    return TG
