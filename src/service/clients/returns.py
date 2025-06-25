"""Modulo para definir devoluciones del servicio de clients: core.clients"""

from pandas import Index, MultiIndex
from core.clients import ClientsPOS
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[ClientsPOS]")
def datajson(value: tuple[ClientsPOS, bool, JsonFrameOrient]):
    """Devolucion de los datos de los clientes."""
    clients, fixed, orientjson = value

    if not isinstance(clients, ClientsPOS):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo ClientsPOS.")

    clients_data = clients.data if fixed else clients.data_pos

    if orientjson:
        data = clients_data.to_json(orient=orientjson)
    else:
        data = clients_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[ClientsPOS]")

@services.opt_return(type="[[[string, string], [number, ...]], ...]")
def analysis(value: dict[tuple[str, str], Index | MultiIndex]):
    """Devolucion de informacion sobre ClientsPOS, donde las llaves son el MapField y los valores
    son los indices de las filas con errores."""
    return ServiceResult({
        "data": [[k, v.to_list()] for k, v in value.items()],
        "type": "[[string, string], [number, ...]]"
    })

@services.opt_return(type="[string|None, string|None, string|None, *[string, ...]]")
def exceptions(value: tuple[str | None, str | None, str | None, *tuple[str, ...]]):
    """Devolucion de informacion sobre los mensajes de errores encontrados en la data ClientsPOS."""
    errs = list(f"{type(e).__name__}: {e}" if isinstance(e, Exception) else None for e in value)
    return ServiceResult({
        "data": errs,
        "type": "[string|None, string|None, string|None, ...[string, ...]]"
    })
