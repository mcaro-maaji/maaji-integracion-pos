"""Modulo para crear los scripts de las caracteristicas principales de la aplicacion."""

__version__ = "1.0.0"
__all__ = ["SERVICES_GROUPS"]

from service import services
from . import cegid

SERVICES_GROUPS = services.groups("scripts", cegid.group)
