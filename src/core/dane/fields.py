"""Modulo para la definicion de los campos de la informacion DANE."""

from enum import StrEnum

class DaneMunicipiosField(StrEnum):
    """Campos de las columnas sobre los codigos postales de la DANE Colombia."""
    DEPARTAMENTO = "DEPARTAMENTO"
    CODIGO_POSTAL = "CODIGO_POSTAL"
    MUNICIPIO = "MUNICIPIO"
