"""
Modulo para gestionar la informacion de la interfaz contable (Accounting Financial Interface).
"""

__version__ = "1.0.0"

__all__ = [
    "fields",
    "exceptions",
    "AFI",
    "AFI_PARAMETERS",
    "AFI_PARAMETERS_UNIQUE",
    "FILENAME_AFI_PARAMETERS",
    "FILEPATH_AFI_PARAMETERS",
    "refresh_afi_paramters",
    "AFITransfers"
]

from . import fields, exceptions
from .afi import AFI
from .paramters import (
    AFI_PARAMETERS,
    AFI_PARAMETERS_UNIQUE,
    FILENAME_AFI_PARAMETERS,
    FILEPATH_AFI_PARAMETERS,
    refresh_afi_paramters
)
from .transfers import AFITransfers
