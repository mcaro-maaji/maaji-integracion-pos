"""Modulo de servicios para gestionar MapFields."""

__version__ = "1.0.0"

__all__ = [
    "mapfields_clients_service",
    "mapfields_services",
    "mapfields_servicesgroup"
]

from service.types import ServicesGroup
from .clients import service as mapfields_clients_service

mapfields_services = [
    mapfields_clients_service
]

mapfields_servicesgroup = ServicesGroup(name="mapfields_group", services=mapfields_services)
