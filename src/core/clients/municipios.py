"""Modulo para la validacion de los municipios en la informacion de los clientes."""

from enum import StrEnum
from pandas import read_csv

class DaneField(StrEnum):
    """Campos de las columnas sobre los codigos postales de la DANE Colombia."""
    DEPARTAMENTO = "DEPARTAMENTO"
    CODIGO_POSTAL = "CODIGO_POSTAL"
    MUNICIPIO = "MUNICIPIO"

PATH_DATA = "../static/dane_municipios.txt"
DANE_MUNICIPIOS = read_csv(PATH_DATA, delimiter=";", dtype=str).fillna("")
