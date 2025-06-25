"""Modulo para la validacion de los municipios en la informacion de los clientes."""

from pandas import read_csv
from utils.constants import PATH_STATIC

PATH_DANE_MUNICIPIOS = PATH_STATIC / "dane_municipios.txt"
DANE_MUNICIPIOS = read_csv(PATH_DANE_MUNICIPIOS, delimiter=";", dtype=str).fillna("")
