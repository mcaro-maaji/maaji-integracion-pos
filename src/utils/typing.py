"""Modulo para de tipado"""

from typing import TypeVar, Iterable, Generic, TypeGuard, Literal
from abc import ABCMeta
from collections import UserString

T = TypeVar("T")

class _NonStringIterableMeta(ABCMeta):
    """Metaclase de NonStringIterable."""
    def __instancecheck__(cls, obj):
        is_iterable = isinstance(obj, Iterable)
        is_string = isinstance(obj, (str, bytes, bytearray, UserString))
        return is_iterable and not is_string

class NonStringIterable(Generic[T], metaclass=_NonStringIterableMeta):
    """Varifica los tipo Iterable y excluye los tipo string."""

def is_dict_string(obj) -> TypeGuard[dict[str, str]]:
    """Comprueba que el valor sea un diccionario de strings en llaves y valores."""
    if not isinstance(obj, dict):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in obj.items())

JsonFrameOrient = Literal[
    "split", "records", "index", "columns", "values", "table"
]

ListJsonFrameOrient: list[JsonFrameOrient] = [
    "split", "records", "index", "columns", "values", "table"
]

REPR_JSONFRAME_ORIENT = "'" + "'|'".join(ListJsonFrameOrient) + "'"
