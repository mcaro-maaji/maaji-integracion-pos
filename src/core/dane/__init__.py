"""Modulo para gestionar informacion necesaria de la DANE para la aplicacion."""

__version__ = "1.0.0"

__all__ = ["DANE_MUNICIPIOS", "DaneMunicipiosField"]

from .municipios import DANE_MUNICIPIOS
from .fields import DaneMunicipiosField
