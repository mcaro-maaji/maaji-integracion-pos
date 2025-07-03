"""Modulo para gestionar informacion de las tiendas y almacenes Maaji para la aplicacion."""

__version__ = "1.0.0"

__all__ = [
    "STORES",
    "STORES_REFUND_ZF",
    "StoreField",
    "FILENAME_STORES",
    "FILEPATH_STORES",
    "refresh_stores"
]

from .stores import STORES, STORES_REFUND_ZF, FILENAME_STORES, FILEPATH_STORES, refresh_stores
from .fields import StoreField
