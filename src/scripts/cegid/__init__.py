"""Modulo para definir scripts utiles al manejar los datos en cegid Y2"""

__version__ = "1.0.0"
__all__ = []

from service import services
from . import params, operations, clients, afi

group = services.group("cegid", operations.service, clients.service, afi.service)
