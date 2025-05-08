"""Modulo que mapea todos los servicios de las caracterisitcas del proyecto."""

__version__ = "1.0.0"

__all__ = [
    "ServiceObj",
    "ServiceOptParameter",
    "ServiceOptReturn",
    "AbsServiceOperation",
    "ServiceOperation",
    "Service",
    "ServicesGroup",
    "ServicesGroups"
]

from .types import (
    ServiceObj,
    ServiceOptParameter,
    ServiceOptReturn,
    ServiceOperation as AbsServiceOperation,
    Service,
    ServicesGroup,
    ServicesGroups
)
from .operation import ServiceOperation
