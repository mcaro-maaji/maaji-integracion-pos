"""Modulo que mapea todos los servicios de las caracterisitcas del proyecto."""

__version__ = "1.0.0"

__all__ = [
    "ServiceObj",
    "Service",
    "ServicesGroup",
    "ServicesGroups",
    "ServiceOptParameter",
    "ServiceOptReturn",
    "ServiceOperation",
    "services",
    "SERVICES_GROUPS"
]

from .types import (
    ServiceObj,
    Service,
    ServicesGroup,
    ServicesGroups
)
from .parameters import ServiceOptParameter, ServiceOptReturn
from .operation import ServiceOperation
from .decorator import services
from . import mapfields, clients

SERVICES_GROUPS = services.groups("groups", mapfields.group, clients.group)
