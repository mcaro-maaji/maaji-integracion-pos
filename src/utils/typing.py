"""Modulo para de tipado"""

from typing import Protocol, TypeVar, Iterator, Union, Iterable, Generic, TypeGuard
from os import PathLike
from abc import ABCMeta
from collections import UserString

T = TypeVar("T")
AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)
AnyStr_contra = TypeVar("AnyStr_contra", str, bytes, contravariant=True)
FilePath = Union[str, PathLike[str]]

class BaseBuffer(Protocol):
    @property
    def mode(self) -> str:
        ...

    def seek(self, __offset: int, __whence: int = ...) -> int:
        ...

    def seekable(self) -> bool:
        ...

    def tell(self) -> int:
        ...


class ReadBuffer(BaseBuffer, Protocol[AnyStr_co]):
    def read(self, __n: int = ...) -> AnyStr_co:
        ...

class ReadCsvBuffer(ReadBuffer[AnyStr_co], Protocol):
    def __iter__(self) -> Iterator[AnyStr_co]:
        ...

    def fileno(self) -> int:
        ...

    def readline(self) -> AnyStr_co:
        ...

    @property
    def closed(self) -> bool:
        ...

class NonStringIterableMeta(ABCMeta):
    """Metaclase de NonStringIterable."""
    def __instancecheck__(cls, obj):
        is_iterable = isinstance(obj, Iterable)
        is_string = isinstance(obj, (str, bytes, bytearray, UserString))
        return is_iterable and not is_string

class NonStringIterable(Generic[T], metaclass=NonStringIterableMeta):
    """Tipo abstracto para tipos Iterables, excluyendo los tipo string."""

def is_dict_str(value) -> TypeGuard[dict[str, str]]:
    """Comprueba que el valor sea un diccionario de strings en llaves y valores."""
    return isinstance(value, dict) and all(isinstance(k, str) and isinstance(v, str)
                                           for k, v in value.items())
