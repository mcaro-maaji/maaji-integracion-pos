"""Modulo para obtener los datos de las tiendas y almancenes Maaji."""

from pandas import read_excel
from utils.constants import PATH_DATA

PATH_PROVIDERS = PATH_DATA / "Proveedores_CEGID_Y2_Retail.xlsx"
PROVIDERS = read_excel(PATH_PROVIDERS, dtype=str).fillna("")
