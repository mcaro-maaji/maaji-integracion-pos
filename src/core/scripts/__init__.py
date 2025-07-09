"""Modulo para gestionar informacion de los scripts para la aplicacion."""

__version__ = "1.0.0"

__all__ = ["fields", "exceptions", "Scripts"]

from . import fields, exceptions
from .scripts import Scripts
