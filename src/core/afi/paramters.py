"""Modulo para obtener los datos de los parametros de la interfaz contable."""

from pandas import read_excel
from data.io import BaseDataIO
from utils.constants import PATH_STATIC_DATA, PATH_DATA
from .fields import AFIParameterField

FILENAME_AFI_PARAMETERS = "Interfaz_Contable_Parametros_CEGID_Y2_Retail.xlsx"
FILEPATH_AFI_PARAMETERS = PATH_STATIC_DATA / FILENAME_AFI_PARAMETERS
AFI_PARAMETERS = BaseDataIO(FILEPATH_AFI_PARAMETERS, support="excel", mode="path")
AFI_PARAMETERS.load(dtype=str)
AFI_PARAMETERS.data.fillna("", inplace=True)

AFIParameterUniqueField = [
    AFIParameterField.MOVIMIENTO,
    AFIParameterField.CODIGO_TIENDA,
    AFIParameterField.COMPROBANTE,
    AFIParameterField.CUENTA,
    AFIParameterField.NATURALEZA,
    AFIParameterField.NIT,
    AFIParameterField.FACTOR,
    AFIParameterField.CECO
]

AFI_PARAMETERS_UNIQUE = BaseDataIO(AFI_PARAMETERS.data[AFIParameterUniqueField].copy())
AFI_PARAMETERS_UNIQUE.load(dtype=str)
AFI_PARAMETERS_UNIQUE.data.fillna("", inplace=True)
AFI_PARAMETERS_UNIQUE.data.drop_duplicates(inplace=True)

def refresh_afi_paramters():
    """Actualiza la informacion de los parametros de interfaz contable"""
    filepath = PATH_DATA / FILENAME_AFI_PARAMETERS

    if not filepath.is_file():
        filepath = FILEPATH_AFI_PARAMETERS

    try:
        data = read_excel(filepath, dtype=str).fillna("")
    except Exception:
        data = read_excel(FILEPATH_AFI_PARAMETERS, dtype=str).fillna("")

    AFI_PARAMETERS.data = data
    AFI_PARAMETERS_UNIQUE.data = AFI_PARAMETERS.data[AFIParameterUniqueField].copy()
