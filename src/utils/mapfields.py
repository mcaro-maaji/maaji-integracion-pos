"""Modulo para la homolacion de campos y datos de tipo string."""

from typing import TypeVar, Generic, overload, Callable
from enum import StrEnum
from collections import UserDict
from re import compile as re_compile
from utils.typing import NonStringIterable, is_dict_str

_KP_co = TypeVar("_KP_co", bound=str, covariant=True) # key primary
_KS_co = TypeVar("_KS_co", bound=str, covariant=True) # key segundary

class MapFieldFunc(StrEnum):
    """Nombre clave de las funciones basicas como criterios de homologacion de datos."""
    EQ = "equal"
    DI = "diferent"
    CO = "content"
    NC = "no content"
    PF = "prefix"
    SF = "suffix"
    RE = "regex"

    def cb(self, data: dict[str, str], default="") -> Callable[[str], str]:
        """Devuelve un callback de la funcion MapField para homologar datos."""

        if self == MapFieldFunc.EQ:
            def callback(value: str):
                if value in data:
                    return data[value]
                return default
        elif self == MapFieldFunc.DI:
            def callback(value: str):
                if value not in data and len(data) > 0:
                    return next(iter(data.values()), default)
                return default
        elif self == MapFieldFunc.CO:
            def callback(value: str):
                for k, v in data.items():
                    if value in k:
                        return v
                return default
        elif self == MapFieldFunc.NC:
            def callback(value: str):
                for k, v in data.items():
                    if value not in k:
                        return v
                return default
        elif self == MapFieldFunc.PF:
            def callback(value: str):
                for k, v in data.items():
                    if k.startswith(value):
                        return v
                return default
        elif self == MapFieldFunc.SF:
            def callback(value: str):
                for k, v in data.items():
                    if k.endswith(value):
                        return v
                return default
        elif self == MapFieldFunc.RE:
            def callback(value: str):
                for k, v in data.items():
                    patter = re_compile(k)
                    if patter.search(value):
                        return v
                return default
        else:
            def callback(__value: str):
                return default

        return callback

class MapData(UserDict):
    """Almacena los datos que se homologan y asignar la funcion aplicable de los mismos."""

    mapfunc: MapFieldFunc

    def __init__(self, *args: str, func: MapFieldFunc, **kwargs: str):
        super().__init__(*args, **kwargs)
        if not is_dict_str(self.data):
            raise TypeError("MapData es de tipo 'dict[str, str]]'")
        self.__mapfunc = func

    @property
    def mapfunc(self):
        return self.__mapfunc

    def __call__(self, *, default: str):
        # FEAT: wrapper control errors to callback
        return self.mapfunc.cb(self.data, default)

class MapFieldData(Generic[_KP_co, _KS_co]):
    """Contiene los datos que se homologan en un MapField, dependiendo de la funcion."""
    __mapfield: tuple[_KP_co, _KS_co]
    __eq: MapData
    __di: MapData
    __co: MapData
    __nc: MapData
    __pf: MapData
    __sf: MapData
    __re: MapData

    def __init__(self, mapfield: tuple[_KP_co, _KS_co]):
        self.__mapfield = mapfield
        self.__eq = MapData(func=MapFieldFunc.EQ)
        self.__di = MapData(func=MapFieldFunc.DI)
        self.__co = MapData(func=MapFieldFunc.CO)
        self.__nc = MapData(func=MapFieldFunc.NC)
        self.__pf = MapData(func=MapFieldFunc.PF)
        self.__sf = MapData(func=MapFieldFunc.SF)
        self.__re = MapData(func=MapFieldFunc.RE)

    @property
    def mapfield(self):
        return self.__mapfield
    @property
    def eq(self):
        return self.__eq
    @property
    def di(self):
        return self.__di
    @property
    def co(self):
        return self.__co
    @property
    def nc(self):
        return self.__nc
    @property
    def pf(self):
        return self.__pf
    @property
    def sf(self):
        return self.__sf
    @property
    def re(self):
        return self.__re

    def lookup(self, default=""):
        """Crea un callback que solo ejecuta la primera funcion MapFieldFunc que contenga datos."""

        if self.eq:
            callback = self.eq(default=default)
        elif self.di:
            callback = self.di(default=default)
        elif self.co:
            callback = self.co(default=default)
        elif self.nc:
            callback = self.nc(default=default)
        elif self.pf:
            callback = self.pf(default=default)
        elif self.sf:
            callback = self.sf(default=default)
        elif self.re:
            callback = self.re(default=default)
        else:
            callback = None

        return callback

class MapFields(Generic[_KP_co, _KS_co], tuple):
    """Mapea los campos con tuplas y los datos en funciones con criterios."""

    # fields line 1 & 2
    #      fields_1          fields_2          fields_1          fields_2
    # [("df_1_column_1", "df_2_column_1"), ("df_1_column_2", "df_2_column_2")]
    __fl_1: tuple[_KP_co]
    __fl_2: tuple[_KS_co]
    __mapdata: dict[tuple[_KP_co, _KS_co], MapFieldData]

    def __new__(cls, *fields: tuple[_KP_co, _KS_co]):
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
    def __getitem__(self, key: tuple[_KP_co, _KS_co] | tuple[str, str]) -> MapFieldData: ...
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
            return self.__mapdata[key]
        raise IndexError(f"No se ha encontrado la llave '{key}' en el MapField.")
