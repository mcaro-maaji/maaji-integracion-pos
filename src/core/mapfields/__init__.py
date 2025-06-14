"""Modulo para la homolacion de campos y datos."""

__version__ = "1.0.0"

__all__ = [
    "MapFieldFunc",
    "MapFieldData",
    "MapData",
    "MapFields"
]

from typing import TypeVar, Generic, overload
from utils.typing import NonStringIterable
from .mapfunc import MapFieldFunc
from .mapdata import MapFieldData, MapData

_KP = TypeVar("_KP", bound=str) # key primary
_KS = TypeVar("_KS", bound=str) # key segundary

class MapFields(Generic[_KP, _KS], tuple):
    """Mapea los campos con tuplas y los datos en funciones con criterios."""

    # fields line 1 & 2
    #      fields_1          fields_2          fields_1          fields_2
    # [("df_1_column_1", "df_2_column_1"), ("df_1_column_2", "df_2_column_2")]
    __fl_1: tuple[_KP]
    __fl_2: tuple[_KS]
    __mapdata: dict[tuple[_KP, _KS], MapFieldData]

    def __new__(cls, *fields: tuple[_KP, _KS]):
        for field in fields:
            if not isinstance(field, NonStringIterable) or len(field) != 2:
                raise TypeError(f"no se define un MapField con el valor: '{field}'")

        obj = super().__new__(cls, fields)
        obj.__fl_1, obj.__fl_2 = zip(*fields)
        obj.__mapdata = {mapfield: MapFieldData(mapfield) for mapfield in fields}
        return obj

    @classmethod
    def from_iterable(cls, *fields: NonStringIterable):
        """Crea una instancia de MapFields desde un iterable y no un mapping de campos."""
        mapfields: MapFields[str, str] = MapFields(*fields)
        return mapfields

    @property
    def fields_1(self):
        """Nombre de los campos principales."""
        return self.__fl_1

    @property
    def fields_2(self):
        """Nombre de los campos que se homologan a los principales."""
        return self.__fl_2

    @overload
    def __getitem__(self, key: int) -> tuple[_KP, _KS]: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[tuple[_KP, _KS], ...]: ...
    @overload
    def __getitem__(self, key: _KP) -> tuple[_KS, ...]: ...
    @overload
    def __getitem__(self, key: _KS) -> tuple[_KP, ...]: ...
    @overload
    def __getitem__(self, key: str) -> tuple[_KP, ...] | tuple[_KS, ...]: ...
    @overload
    def __getitem__(self, key: tuple[_KP, _KS] | tuple[str, str]) -> MapFieldData: ...
    def __getitem__(self, key: int | slice | tuple[_KP, _KS] | _KP | _KS):
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)

        if isinstance(key, str):
            if key in self.fields_1:
                return tuple(self.fields_2[idx] for idx, v in enumerate(self.fields_1) if v == key)
            if key in self.fields_2:
                return tuple(self.fields_1[idx] for idx, v in enumerate(self.fields_2) if v == key)
            return tuple()

        if isinstance(key, tuple):
            return self.__mapdata[key]
        raise IndexError(f"No se ha encontrado la llave '{key}' en el MapField")
