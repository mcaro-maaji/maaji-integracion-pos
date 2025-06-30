"""Modulo para gestionar las facturas de compra, integracion con POS CEGID Y2 Retail."""

__version__ = "1.0.0"

__all__ = ["fields", "exceptions", "Bills"]

from . import fields, exceptions
from .bills import Bills
