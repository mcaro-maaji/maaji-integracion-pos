"""Modulo para obtener los datos de las tiendas y almancenes Maaji."""

from pandas import read_excel
from utils.constants import PATH_DATA

PATH_STORES = PATH_DATA / "Tiendas_CEGID_Y2_Retail.xlsx"
STORES = read_excel(PATH_STORES, dtype=str).fillna("")
