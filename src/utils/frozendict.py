"""Modulo de utilidad para tener diccionarios inmutables."""

from typing import Generic, TypeVar
from types import MappingProxyType

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

class FrozenDict(Generic[_KT, _VT], dict):
    """Crea un diccionario inmutable."""
    __slots__ = ('__data', '__hash')
    __data: MappingProxyType[_KT, _VT]
    __hash: int

    def __new__(cls, *args: tuple[_KT, _VT], **kwargs: _VT):
        obj = super().__new__(cls)
        raw_data: dict[_KT, _VT] = dict(*args, **kwargs)
        obj.__data = MappingProxyType(raw_data)
        return obj

    def __getitem__(self, key):
        return self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self.__data)})"

    def __contains__(self, key):
        return key in self.__data

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def items(self):
        return self.__data.items()

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def copy(self, **add_or_replace):
        """Devuelve una copia del FrozenDict, con cambios opionales."""
        new_data = dict(self.__data)
        new_data.update(add_or_replace)
        return self.__class__(new_data)

    def __eq__(self, other):
        if isinstance(other, FrozenDict):
            return dict(self.__data) == dict(other.__data)
        if isinstance(other, dict):
            return dict(self.__data) == other
        return NotImplemented

    def __hash__(self):
        if self.__hash is None:
            # Convertimos los items a un frozenset para calcular el hash
            self.__hash = hash(frozenset(self.__data.items()))
        return self.__hash

    # Bloqueamos cualquier operación de escritura
    def __setitem__(self, key, value):
        raise TypeError("FrozenDict is immutable")

    def __delitem__(self, key):
        raise TypeError("FrozenDict is immutable")

    def clear(self):
        raise TypeError("FrozenDict is immutable")

    def pop(self, key, default=None):
        raise TypeError("FrozenDict is immutable")

    def popitem(self):
        raise TypeError("FrozenDict is immutable")

    def setdefault(self, key, default=None):
        raise TypeError("FrozenDict is immutable")

    def update(self, *args, **kwargs):
        raise TypeError("FrozenDict is immutable")
