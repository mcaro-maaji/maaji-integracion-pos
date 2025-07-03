"""Modulo para obtener los datos de las tiendas y almancenes Maaji."""

from pandas import read_excel
from data.io import BaseDataIO
from utils.constants import PATH_STATIC_DATA, PATH_DATA

FILENAME_PROVIDERS = "Proveedores_CEGID_Y2_Retail.xlsx"
FILEPATH_PROVIDERS = PATH_STATIC_DATA / FILENAME_PROVIDERS
PROVIDERS = BaseDataIO(FILEPATH_PROVIDERS, support="excel", mode="path")
PROVIDERS.load(dtype=str)
PROVIDERS.data.fillna("", inplace=True)

def refresh_providers():
    """Actualiza la informacion de los proveedores"""
    filepath = PATH_DATA / FILENAME_PROVIDERS

    if not filepath.is_file():
        filepath = FILEPATH_PROVIDERS

    try:
        data = read_excel(filepath, dtype=str).fillna("")
    except Exception:
        data = read_excel(FILEPATH_PROVIDERS, dtype=str).fillna("")

    PROVIDERS.data = data
