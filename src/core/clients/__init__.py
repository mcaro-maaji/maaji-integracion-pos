"""Modulo para gestionar la informacion de los clientes.
Spec: 01. feature-analizador-info-clientes-pos.docx
"""

from .clients import Clients
from .pos import ClientsPOS
from .municipios import DANE_MUNICIPIOS, DaneField
from .pos_cegid import ClientsCegid, MAPFIELDS_POS_CEGID
from .fields import (
    ClientField,
    ClientFieldShopifyMx,
    ClientShopifyJson,
    ClientShopifyJsonAddress,
    ClientShopifyJsonMetaField
)
from .exceptions import (ClientsException,
    ClientsWarning,
    NoMatchClientFieldsWarning,
    IncorrectClientFieldsWarning,
    MaxClientsWarning,
    WARNING_MAX_CLIENTS
)

__version__ = "1.0.0"

__all__ = [
    "Clients",
    "ClientsPOS",
    "DANE_MUNICIPIOS",
    "DaneField",
    "ClientsCegid",
    "MAPFIELDS_POS_CEGID",
    "ClientField",
    "ClientFieldShopifyMx",
    "ClientShopifyJson",
    "ClientShopifyJsonAddress",
    "ClientShopifyJsonMetaField",
    "ClientsException",
    "ClientsWarning",
    "NoMatchClientFieldsWarning",
    "IncorrectClientFieldsWarning",
    "MaxClientsWarning",
    "WARNING_MAX_CLIENTS"
]
