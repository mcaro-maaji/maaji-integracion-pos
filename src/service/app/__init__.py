"""Modulo para crear los servicios de la caracteristicas de los clientes."""

__version__ = "1.0.0"

__all__ = ["session"]

from service.decorator import services
from . import session, commands

group = services.group("app", session.service, commands.service)
