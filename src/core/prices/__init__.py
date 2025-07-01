"""Modulo para gestionar los precios de venta, integracion con POS CEGID Y2 Retail."""

__version__ = "1.0.0"

__all__ = ["fields", "exceptions", "Prices"]

from . import fields, exceptions
from .prices import Prices
