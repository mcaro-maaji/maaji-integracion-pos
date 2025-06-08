"""Modulo de servicios para gestionar MapFields."""

__version__ = "1.0.0"

__all__ = [
    "service_clients",
    "group_mapfields",
]

from service.decorator import services
from .clients import service_clients

group_mapfields = services.group("mapfields", service_clients)
