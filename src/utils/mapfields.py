"""Modulo para la homolacion de campos de los DataFrame."""

from typing import TypeVar, Generic, overload, Callable
from types import MappingProxyType as FreezeDict
from enum import StrEnum

_KP_co = TypeVar("_KP_co", bound=str, covariant=True) # key primary
_KS_co = TypeVar("_KS_co", bound=str, covariant=True) # key segundary

class MapFieldsFunc(StrEnum):
    """Nombre clave de las funciones basicas como criterios de homologacion de datos."""
    IS = "is condition"
    EQ = "equal"
    DI = "diferent"
    CO = "content"
    NC = "no content"
    PF = "prefix"
    SF = "suffix"
    IN = "inplace"
    WO = "with out"

MapFieldsData = tuple[MapFieldsFunc, dict[str, str]]

class MapFields(Generic[_KP_co, _KS_co], tuple):
    """Mapea los campos de los DataFrames con tuplas y los datos en funciones con criterios."""

    # fields line 1 & 2
    #      fields_1          fields_2          fields_1          fields_2
    # [("df_1_column_1", "df_2_column_1"), ("df_1_column_2", "df_2_column_2")]
    __fl_1: tuple[_KP_co]
    __fl_2: tuple[_KS_co]
    __mapdata: dict[tuple[_KP_co, _KS_co], list[MapFieldsData]]

    def __new__(cls, *fields: tuple[_KP_co, _KS_co],
                mapdata: dict[tuple[_KP_co, _KS_co], list[MapFieldsData]] = None):
        if mapdata is None:
            mapdata = {}
        fields = (*fields, *mapdata.keys())
        return super().__new__(cls, fields)

    def __init__(self, *__fields: tuple[_KP_co, _KS_co],
                 mapdata: dict[tuple[_KP_co, _KS_co], list[MapFieldsData]] = None):
        if mapdata is None:
            mapdata = {}
        self.__fl_1, self.__fl_2 = zip(*self)
        self.__mapdata = FreezeDict(mapdata)

    @property
    def fields_1(self):
        """Nombre de los campos principales."""
        return self.__fl_1

    @property
    def fields_2(self):
        """Nombre de los campos que se homologan a los principales."""
        return self.__fl_2

    @property
    def mapdata(self):
        """Datos y funcion que se va aplicar para homologar los datos de un df."""
        return self.__mapdata

    @overload
    def __getitem__(self, key: int) -> tuple[_KP_co, _KS_co]: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[tuple[_KP_co, _KS_co], ...]: ...
    @overload
    def __getitem__(self, key: _KP_co) -> tuple[_KS_co, ...]: ...
    @overload
    def __getitem__(self, key: _KS_co) -> tuple[_KP_co, ...]: ...
    @overload
    def __getitem__(self, key: str) -> tuple[_KP_co, ...] | tuple[_KS_co, ...]: ...
    @overload
    def __getitem__(self, key: tuple[_KP_co, _KS_co] | tuple[str, str]) -> list[MapFieldsData]: ...
    def __getitem__(self, key: int | slice | tuple[_KP_co, _KS_co] | _KP_co | _KS_co):
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)

        if isinstance(key, str):
            if key in self.fields_1:
                return tuple(self.fields_2[idx] for idx, v in enumerate(self.fields_1) if v == key)
            if key in self.fields_2:
                return tuple(self.fields_1[idx] for idx, v in enumerate(self.fields_2) if v == key)
            return tuple()

        if isinstance(key, tuple):
            return self.mapdata[key]
        raise IndexError(f"No se ha encontrado la llave '{key}' en el MapField.")

    @overload
    def getkey(self, key: tuple[_KP_co, _KS_co]) -> tuple[_KP_co, _KS_co]: ...
    @overload
    def getkey(self, field_1: _KP_co, field_2: _KS_co) -> tuple[_KP_co, _KS_co]: ...
    def getkey(self, key_or_field_1, field_2 = None):
        """Llave para acceder al mapeo de datos."""

        if isinstance(key_or_field_1, str) and isinstance(field_2, str):
            key: tuple[_KP_co, _KS_co] = (key_or_field_1, field_2)
        else:
            key: tuple[_KP_co, _KS_co] = key_or_field_1
        return key

    def getmapdata(self, mapfield: tuple[_KP_co, _KS_co], *, func: MapFieldsFunc) -> dict[str, str]:
        """Halla los datos que se homologan de los campos."""

        if mapfield not in self:
            raise IndexError(f"No se ha mapeado una funcion MapFieldData con la llave '{mapfield}'")

        list_mapdata = self[mapfield]
        return {k: v for m in list_mapdata if m[0] == func for k, v in m[1].items()}

    def eq(self, mapfield: tuple[_KP_co, _KS_co], *, default="") -> Callable[[str], str]:
        """Compara los valores de mapdata por igual y devuelve un callback aplicable en un df."""

        mapdata = self.getmapdata(mapfield, func=MapFieldsFunc.EQ)
        def callback(value: str):
            if value in mapdata:
                return mapdata[value]
            return default
        return callback

    def exec(self, mapfield: tuple[_KP_co, _KS_co], func: MapFieldsFunc, *,
                  default="") -> Callable[[str], str]:
        """Devuleve el callback aplicable segun la funcion ejecutada."""

        def callback(__value: str):
            return default

        if func == MapFieldsFunc.EQ:
            callback = self.eq(mapfield, default=default)
        # elif mapfunc == MapFieldsFunc.IS:
        # elif mapfunc == MapFieldsFunc.DI:
        # elif mapfunc == MapFieldsFunc.CO:
        # elif mapfunc == MapFieldsFunc.NC:
        # elif mapfunc == MapFieldsFunc.PF:
        # elif mapfunc == MapFieldsFunc.SF:
        # elif mapfunc == MapFieldsFunc.IN:
        # elif mapfunc == MapFieldsFunc.WO:
        return callback

    def getfuncs(self, mapfield: tuple[_KP_co, _KS_co]) -> tuple[MapFieldsFunc]:
        """Devuelve los tipos de MapFieldsFunc mapeados en el campo que homologa datos."""
        funcs = set([] if mapfield not in self.mapdata else i[0] for i in self.mapdata[mapfield])
        return tuple(funcs)

    def multi_funcs(self, mapfield: tuple[_KP_co, _KS_co], *, default: str = ""
                    ) -> dict[MapFieldsFunc, Callable[[str], str]]:
        """Devuelve todas las funciones aplicables en un DF del campo homologado."""
        return {mf: self.exec(mapfield, mf, default=default) for mf in self.getfuncs(mapfield)}
