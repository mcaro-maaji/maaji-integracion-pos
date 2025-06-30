"""Modulo para la definicion de los campos de los proveedores Maaji."""

from enum import StrEnum

class ProviderField(StrEnum):
    """Campos de las columnas sobre los proveedores con informacion basica."""
    CODIGO = "Codigo"
    RAZON_SOCIAL = "Razon Social"
    CODIGO_POSTAL = "Codigo Postal"
