"""Modulo para gestionar informacion de las tiendas y almacenes Maaji para la aplicacion."""

__version__ = "1.0.0"

__all__ = ["STORES", "STORES_REFUND_ZF", "StoreField"]

from .stores import STORES, STORES_REFUND_ZF
from .fields import StoreField
