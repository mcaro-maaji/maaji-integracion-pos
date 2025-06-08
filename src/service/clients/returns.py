"""Modulo para definir devoluciones del servicio de clients: core.clients"""

from core.clients import ClientsPOS
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[ClientsPOS]")
def datajson(value: tuple[ClientsPOS, bool, JsonFrameOrient]):
    """Devolucion de los datos de los clientes."""
    clients, converted, orient = value

    if not isinstance(clients, ClientsPOS):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo ClientsPOS.")

    if converted:
        data = clients.data.to_json(orient=orient)
    else:
        data = clients.data_pos.to_json(orient=orient)

    return ServiceResult(data=data, type="JsonOriented[ClientsPOS]")
