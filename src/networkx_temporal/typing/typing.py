from sys import version_info

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

class _FigureType:
    def __repr__(self):
        return "Figure"
_FigureType = _FigureType()

class _StaticGraphType:
    def __repr__(self):
        return "Graph"
_StaticGraphType = _StaticGraphType()

class _TemporalGraphType:
    def __repr__(self):
        return "TemporalGraph"
_TemporalGraphType = _TemporalGraphType()

if version_info[1] >= 11:
    from typing import TypeAlias
    Figure: TypeAlias = _FigureType
    StaticGraph: TypeAlias = _StaticGraphType
    TemporalGraph: TypeAlias = _TemporalGraphType
else:
    Figure = type(_FigureType)
    StaticGraph = type(_StaticGraphType)
    TemporalGraph = type(_TemporalGraphType)

Literal.__doc__ = "Type hint for ``typing.Literal`` with Python 3.7 support."
Figure.__doc__ = "Type hint for ``matplotlib.figure.Figure`` objects."
StaticGraph.__doc__ = "Type hint for any ``networkx`` graph objects."
TemporalGraph.__doc__ = "Type hint for any ``networkx_temporal`` graph objects."
