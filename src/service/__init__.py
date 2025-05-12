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
from .mapfields import mapfields_servicesgroup
from .clients import clients_servicesgroup

services_groups = [
    mapfields_servicesgroup,
    clients_servicesgroup
]

SERVICES_GROUPS = ServicesGroups(name="services_groups", services_groups=services_groups)
