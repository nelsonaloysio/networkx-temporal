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


try:
    from matplotlib.pyplot import Figure
except ModuleNotFoundError:
    class Figure:
        ...


class TemporalGraph:
    ...


TemporalDiGraph = TemporalMultiGraph = TemporalMultiDiGraph = TemporalGraph
