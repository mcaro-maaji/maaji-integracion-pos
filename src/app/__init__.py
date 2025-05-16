"""Modulo para crear la aplicacion web y api de las funcionalidades."""

from .app import app
from .routes import *
from .server import server

__version__ = "1.0.0"

__all__ = ["app", "server"]
