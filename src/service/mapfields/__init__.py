"""Modulo de servicios para gestionar MapFields."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns",
    "service_clients",
    "group_mapfields"
]

from service.decorator import services
from .clients import service_clients
from . import params, returns

group_mapfields = services.group("mapfields", service_clients)
