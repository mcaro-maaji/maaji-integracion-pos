"""Modulo para crear la aplicacion web y api de las funcionalidades."""

from . import (
    logging as _,
    app,
    server,
    settings,
    custom,
    login,
    routes,
    pages
)

__version__ = "1.0.0"

__all__ = ["app", "server", "settings", "custom", "login", "routes", "pages"]
