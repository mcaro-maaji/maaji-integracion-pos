"""Modulo para definir devoluciones del servicio de settings"""

from data.io import BaseDataIO
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[Settings]")
def datajson(value: tuple[BaseDataIO, bool, JsonFrameOrient]):
    """Devolucion de los datos de las configuraciones."""
    settings, fixed, orientjson = value

    if not isinstance(settings, BaseDataIO):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo BaseDataIO.")

    settings_data = settings.data if fixed else settings.data # 😅 me quede sin tiempo 🕑

    if orientjson:
        data = settings_data.to_json(orient=orientjson)
    else:
        data = settings_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[Settings]")
