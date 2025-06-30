"""Modulo para la validacion de los municipios en Colombia."""

from pandas import read_excel
from utils.constants import PATH_DATA

PATH_DANE_MUNICIPIOS = PATH_DATA / "Dane_Municipios.xlsx"
DANE_MUNICIPIOS = read_excel(PATH_DANE_MUNICIPIOS, dtype=str).fillna("")
