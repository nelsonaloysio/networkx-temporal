from sys import version_info
assert version_info.major == 3

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


class _TemporalDiGraphType:
    def __repr__(self):
        return "TemporalDiGraph"
_TemporalDiGraphType = _TemporalDiGraphType()


class _TemporalMultiGraphType:
    def __repr__(self):
        return "TemporalMultiGraph"
_TemporalMultiGraphType = _TemporalMultiGraphType()


class _TemporalMultiDiGraphType:
    def __repr__(self):
        return "TemporalMultiDiGraph"
_TemporalMultiDiGraphType = _TemporalMultiDiGraphType()


if version_info.minor >= 11:
    from typing import TypeAlias
    Figure: TypeAlias = _FigureType
    StaticGraph: TypeAlias = _StaticGraphType
    TemporalGraph: TypeAlias = _TemporalGraphType
    TemporalDiGraph: TypeAlias = _TemporalDiGraphType
    TemporalMultiGraph: TypeAlias = _TemporalMultiGraphType
    TemporalMultiDiGraph: TypeAlias = _TemporalMultiDiGraphType
else:
    Figure = type(_FigureType)
    StaticGraph = type(_StaticGraphType)
    TemporalGraph = type(_TemporalGraphType)
    TemporalDiGraph = type(_TemporalDiGraphType)
    TemporalMultiGraph = type(_TemporalMultiGraphType)
    TemporalMultiDiGraph = type(_TemporalMultiDiGraphType)

classes = "networkx_temporal.classes"

Literal.__doc__ = "Type for ``typing.Literal`` with Python 3.7 support."
Figure.__doc__ = "Type for ``matplotlib.figure.Figure`` objects."
StaticGraph.__doc__ = "Type for any ``networkx`` graph objects."
TemporalGraph.__doc__ = f"Type for :class:`~{classes}.TemporalGraph` objects."
TemporalDiGraph.__doc__ = f"Type for :class:`~{classes}.TemporalDiGraph` objects."
TemporalMultiGraph.__doc__ = f"Type for :class:`~{classes}.TemporalMultiGraph` objects."
TemporalMultiDiGraph.__doc__ = f"Type for :class:`~{classes}.TemporalMultiDiGraph` objects."
