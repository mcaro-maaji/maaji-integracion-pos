"""Modulo para definir parametros de las caracteristicas db"""

from service.decorator import services
from data.io import (
    DataIO, is_dataio,
    SupportDataIO, ListSupportDataIO, REPR_SUPPORT_DATAIO,
    ModeDataIO, ListModeDataIO, REPR_MODE_DATAIO
)

@services.parameter(type="DataIO")
def source(value: DataIO):
    """Parametro para validar la fuente de datos."""
    if is_dataio(value):
        return value
    raise TypeError("el origen de los datos debe ser de tipo DataIO")

@services.parameter(type="DataIO")
def destination(value: DataIO):
    """Parametro para validar el soporte del destino de los datos."""
    if is_dataio(value):
        return value
    raise TypeError("el destino de los datos debe ser de tipo DataIO")

@services.parameter(type=REPR_SUPPORT_DATAIO)
def support(value: SupportDataIO):
    """Parametro para validar el soporte de lectura y escritura de datos."""
    if value in ListSupportDataIO:
        return value
    msg = "el soporte del origen DataIO debe ser uno de estos valores: " + REPR_SUPPORT_DATAIO
    raise TypeError(msg)

@services.parameter(type=REPR_MODE_DATAIO)
def mode(value: ModeDataIO):
    """Parametro para validar el modo de acceso a los datos."""
    if value in ListModeDataIO:
        return value
    msg = "el modo del origen DataIO debe ser uno de estos valores: " + REPR_MODE_DATAIO
    raise TypeError(msg)
