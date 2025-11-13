"""
Top-level module for the package.

.. rubric:: Summary

.. autosummary::

   algorithms
   classes
   drawing
   generators
   readwrite
   transform
   typing
   utils

.. rubric:: Note

Some classes and functions are exposed at the top level for convenience and may also be accessed via the
individual modules. For example, the :class:`~networkx_temporal.classes.TemporalGraph` class
can be imported by running:

.. code-block:: python

    >>> from networkx_temporal import TemporalGraph

Or, alternatively, from the :mod:`~networkx_temporal.classes` module in which it is defined:

.. code-block:: python

    >>> from networkx_temporal.classes import TemporalGraph

For detailed information on each class and function, please refer to the individual modules.
"""

from .__version__ import __version__
from .algorithms import *
from .classes import *
from .drawing import *
from .generators import *
from .readwrite import *
from .transform import *
from .utils import *
from .utils.convert import *
