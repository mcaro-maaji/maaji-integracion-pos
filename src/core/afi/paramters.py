"""Modulo para obtener los datos de los parametros de la interfaz contable."""

from pandas import read_excel
from utils.constants import PATH_DATA
from .fields import AFIParameterField

PATH_AFI_PARAMETERS = PATH_DATA / "Interfaz_Contable_Parametros_CEGID_Y2_Retail.xlsx"
AFI_PARAMETERS = read_excel(PATH_AFI_PARAMETERS, dtype=str).fillna("")
AFI_PARAMETERS_UNIQUE = AFI_PARAMETERS[[
    AFIParameterField.MOVIMIENTO,
    AFIParameterField.CODIGO_TIENDA,
    AFIParameterField.COMPROBANTE,
    AFIParameterField.CUENTA,
    AFIParameterField.NATURALEZA,
    AFIParameterField.NIT,
    AFIParameterField.FACTOR,
    AFIParameterField.CECO
]].copy()
AFI_PARAMETERS_UNIQUE.drop_duplicates(inplace=True)
