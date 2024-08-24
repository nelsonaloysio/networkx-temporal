try:
    from importlib.metadata import version
    __version__ = version("networkx_temporal")
except ImportError: # <= Python 3.7
    from os.path import abspath, dirname
    PATH = abspath(f"{dirname(__file__)}/../..")
    with open(f"{PATH}/pyproject.toml") as f:
        __version__ = f.read().split("version = ", 1)[-1].split("\n", 1)[0].strip('"')
