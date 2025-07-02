"""Modulo para disponer de todos los recursos en la web a modo de servicios."""

__version__ = "1.0.0"

from service import services
from . import clients, bills

SERVICES_GROUP = services.group("web", clients.service, bills.service)
