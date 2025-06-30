"""Modulo para gestionar la informacion de los clientes.
Spec: 01. feature-analizador-info-clientes-pos.docx
Spec: 02. feature-map-info-clientes-shopify-pos.docx
"""

__version__ = "1.0.0"

__all__ = [
    "fields",
    "exceptions",
    "Clients",
    "ClientsPOS",
    "ClientsCegid",
    "MAPFIELDS_CLIENTS_POS_CEGID",
    "ClientsShopify",
    "MAPFIELDS_CLIENTS_POS_SHOPIFY"
]

from . import fields, exceptions
from .clients import Clients
from .pos import ClientsPOS
from .pos_cegid import ClientsCegid, MAPFIELDS_CLIENTS_POS_CEGID
from .pos_shopify import ClientsShopify, MAPFIELDS_CLIENTS_POS_SHOPIFY
