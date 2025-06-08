"""Modulo para crear la aplicacion web y api de las funcionalidades."""

from .app import app
from .server import server, config_server
from .routes import *
from .config import *

__version__ = "1.0.0"

__all__ = ["app", "server", "config_server"]
