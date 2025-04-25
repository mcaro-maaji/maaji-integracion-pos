"""Modulo para extender las funcionalidades de los dataclasses."""

from typing import TypeVar, Type
from dataclasses import fields

T = TypeVar("T")

def dict_to_dtcls(cls: Type[T], raw_dict: dict) -> T:
    """Convierte un dict a un dataclass ignorando los campos que no coincidan."""
    field_names = {f.name for f in fields(cls)}
    limpio = {k: v for k, v in raw_dict.items() if k in field_names}
    return cls(**limpio)
