"""Modulo para crear automatizaciones de la aplicacion y a nivel de sistema."""

__version__ = "1.0.0"

__all__ = ["SERVICE_GROUP", "scripts"]

from service import services
from . import scripts

SERVICE_GROUP = services.group("auto", scripts.service)
