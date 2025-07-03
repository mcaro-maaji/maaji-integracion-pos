"""Modulo para crear los servicios de la caracteristicas de los precios de venta."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns",
    "data",
    "cegid"
]

from service.decorator import services
from . import params, returns, data, cegid

group = services.group("prices", cegid.service)
