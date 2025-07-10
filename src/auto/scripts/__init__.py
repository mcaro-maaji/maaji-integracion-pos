"""Modulo para gestionar la automatizacion de los scripts."""

__version__ = "1.0.0"

__all__ = [
    "params",
    "returns",
    "execute",
    "service"
]

from . import params, returns
from .execute import execute
from .services import service
