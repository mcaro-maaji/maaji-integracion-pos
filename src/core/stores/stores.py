"""Modulo para obtener los datos de las tiendas y almancenes Maaji."""

from pandas import read_excel
from data.io import BaseDataIO
from utils.constants import PATH_STATIC_DATA, PATH_DATA
from .fields import StoreField

FILENAME_STORES = "Tiendas_CEGID_Y2_Retail.xlsx"
FILEPATH_STORES = PATH_STATIC_DATA / FILENAME_STORES
STORES = BaseDataIO(FILEPATH_STORES, support="excel", mode="path")
STORES.load(dtype=str)
STORES.data.fillna("", inplace=True)

filter_mas_devoluciones = STORES.data[StoreField.NOMBRE_TIENDA].str.startswith("MAS DEVOLUCIONES")
STORES_REFUND_ZF = BaseDataIO(STORES.data[filter_mas_devoluciones].copy())
STORES_REFUND_ZF.load(dtype=str)
STORES_REFUND_ZF.data.fillna("", inplace=True)

def refresh_stores():
    """Actualiza la informacion de los proveedores"""
    filepath = PATH_DATA / FILENAME_STORES

    if not filepath.is_file():
        filepath = FILEPATH_STORES

    try:
        data = read_excel(filepath, dtype=str).fillna("")
    except Exception:
        data = read_excel(FILEPATH_STORES, dtype=str).fillna("")

    STORES.data = data
    STORES_REFUND_ZF.data = STORES.data[filter_mas_devoluciones].copy()
