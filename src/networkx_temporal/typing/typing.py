from typing import TypeAlias, Union

try:
    from typing import Literal
except ImportError: # Python < 3.8
    from typing import _GenericAlias, _SpecialForm
    class _LiteralForm(_SpecialForm, _root=True):
        def __repr__(self):
            return "typing_extensions." + self._name
        def __getitem__(self, parameters):
            return _GenericAlias(self, parameters)
    Literal = _LiteralForm("Literal", doc="typing_extensions.Literal")
Literal.__doc__ = "Type hint for ``typing.Literal`` with Python 3.7 support."

import networkx as nx

class _FigureType:
    def __repr__(self):
        return "matplotlib.figure.Figure"
_FigureType = _FigureType()

class _TemporalGraphType:
    def __repr__(self):
        return "networkx_temporal.TemporalGraph"
_TemporalGraphType = _TemporalGraphType()

Figure: TypeAlias = _FigureType
Figure.__doc__ = "Type hint for ``matplotlib.figure.Figure`` objects."

StaticGraph: TypeAlias = Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
StaticGraph.__doc__ = "Union type hint for any ``networkx`` graph objects."

TemporalGraph: TypeAlias = _TemporalGraphType
TemporalGraph.__doc__ = "Type hint for any ``networkx_temporal`` graph objects."
