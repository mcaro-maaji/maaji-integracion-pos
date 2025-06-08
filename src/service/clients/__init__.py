"""Modulo para crear los servicios de la caracteristicas de los clientes."""

__version__ = "1.0.0"

__all__ = [
    "service_cegid",
    "group_clients",
]

from service.decorator import services
from .cegid import service_cegid
from .shopify import service_shopify

group_clients = services.group("clients", service_cegid, service_shopify)
