"""Modulo para la validacion de los municipios en Colombia."""

from pandas import read_excel
from data.io import BaseDataIO
from utils.constants import PATH_STATIC_DATA, PATH_DATA

FILENAME_DANE_MUNICIPIOS = "Dane_Municipios.xlsx"
FILEPATH_DANE_MUNICIPIOS = PATH_STATIC_DATA / FILENAME_DANE_MUNICIPIOS
DANE_MUNICIPIOS = BaseDataIO(FILEPATH_DANE_MUNICIPIOS, support="excel", mode="path")
DANE_MUNICIPIOS.load(dtype=str)
DANE_MUNICIPIOS.data.fillna("", inplace=True)

def refresh_dane_municipios():
    """Actualiza la informacion de los municipios"""
    filepath = PATH_DATA / FILENAME_DANE_MUNICIPIOS

    if not filepath.is_file():
        filepath = FILEPATH_DANE_MUNICIPIOS

    try:
        data = read_excel(filepath, dtype=str).fillna("")
    except Exception:
        data = read_excel(FILEPATH_DANE_MUNICIPIOS, dtype=str).fillna("")

    DANE_MUNICIPIOS.data = data
