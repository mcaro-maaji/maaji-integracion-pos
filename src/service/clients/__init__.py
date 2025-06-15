"""Modulo para crear los servicios de la caracteristicas de los clientes."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns",
    "cegid",
    "shopify"
]

from service.decorator import services
from . import params, returns, data, cegid, shopify

group = services.group("clients", cegid.service, shopify.service)
