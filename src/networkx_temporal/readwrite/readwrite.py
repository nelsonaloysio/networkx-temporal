import os.path as osp
from io import BufferedReader, BufferedWriter, BytesIO
from typing import Callable, Optional, Union

import networkx as nx

from .hif import read_hif
from ..typing import Literal

READER = {
    "hif": read_hif,
}

def _get_filepath(
    file: Optional[Union[str, BufferedReader, BufferedWriter, BytesIO]]
) -> Union[str, None]:
    """
    Returns file path from file object or string, if available.
    """
    return file if type(file) == str else file.name if hasattr(file, "name") else None


def _get_filename(path: Optional[str]) -> Union[str, None]:
    """
    Returns file name from path, if it is a string.
    """
    name = None
    if path is not None:
        name = osp.splitext(osp.basename(path[:-4] if path.endswith(".zip") else path))[0]
    return name


def _get_format(
    path: Optional[str],
    frmt: Optional[Union[str, Callable]] = None
) -> Union[str, None]:
    """
    Returns file format from path, if it is a string.
    """
    if callable(frmt):
        return frmt
    elif type(path) == str:
        if path.lower().endswith(".hif.json"):
            # filename.hif.json
            return "hif"
        frmt = osp.splitext(path[:-4] if path.endswith(".zip") else path)[-1]
        frmt = frmt.lower().lstrip(".")
        return frmt
    return None


def _get_format_ext(frmt: Optional[str]) -> str:
    """
    Returns file format extension, if available.
    """
    ext = ""
    if frmt == "hif":
        # filename.hif.json
        ext = ".hif.json"
    elif type(frmt) == str:
        ext = f".{frmt}"
    elif callable(frmt) and any(frmt.__name__.startswith(_) for _ in ("generate_", "write_")):
        ext = f".{frmt.__name__.split('_', 1)[-1]}"
    return ext


def _get_function(
    frmt: Union[str, Callable],
    prefix: Literal["generate", "read", "write"]
) -> Union[Callable, None]:
    """
    Returns generator, reader, or writer function, if format is a string.
    """
    if callable(frmt):
        return frmt
    if type(frmt) == str:
        if frmt in READER and prefix == "read":
            return READER[frmt]
        return getattr(nx, f"{prefix}_{frmt}", None)
    return None
