"""Modulo para organizar los datos que se van a homologar."""

from typing import TypeVar, Generic
from collections import UserDict
from utils.typing import is_dict_string
from .mapfunc import MapFieldFunc

_KP = TypeVar("_KP", bound=str) # key primary
_KS = TypeVar("_KS", bound=str) # key segundary

class MapData(UserDict):
    """Almacena los datos que se homologan y asignar la funcion aplicable de los mismos."""
    mapfunc: MapFieldFunc

    def __init__(self, *args: str, func: MapFieldFunc, **kwargs: str):
        super().__init__(*args, **kwargs)
        if not is_dict_string(self.data):
            raise TypeError("MapData es de tipo 'dict[str, str]]'")
        self.__mapfunc = func

    @property
    def mapfunc(self):
        return self.__mapfunc

    def __call__(self, *, default: str):
        # FEAT: wrapper control errors to callback
        return self.mapfunc.cb(self.data, default)

class MapFieldData(Generic[_KP, _KS]):
    """Contiene los datos que se homologan en un MapField, dependiendo de la funcion."""
    __mapfield: tuple[_KP, _KS]
    __eq: MapData
    __di: MapData
    __co: MapData
    __nc: MapData
    __pf: MapData
    __sf: MapData
    __re: MapData

    def __init__(self, mapfield: tuple[_KP, _KS]):
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
