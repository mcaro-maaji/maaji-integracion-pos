"""Modulo para crear los servicios de la caracteristicas de los clientes."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns",
    "data",
    "cegid"
]

from service.decorator import services
from . import params, returns, data, cegid

group = services.group("afi", cegid.service)
