"""Modulo para gestionar los productos, integracion con POS CEGID Y2 Retail."""

__version__ = "1.0.0"

__all__ = ["fields", "exceptions", "Products"]

from . import fields, exceptions
from .products import Products
