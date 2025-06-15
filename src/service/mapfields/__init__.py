"""Modulo de servicios para gestionar MapFields."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns"
]

from service.decorator import services
from . import params, returns, clients

group = services.group("mapfields", clients.service)
