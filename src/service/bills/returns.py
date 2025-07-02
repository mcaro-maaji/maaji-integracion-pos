"""Modulo para definir devoluciones del servicio de bills: core.bills"""

from pandas import Index, MultiIndex
from core.bills import Bills
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[Bills]")
def datajson(value: tuple[Bills, bool, JsonFrameOrient]):
    """Devolucion de los datos de los clientes."""
    bills, fixed, orientjson = value

    if not isinstance(bills, Bills):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo Bills.")

    bills_data = bills.data if fixed else bills.data # 😅 me quede sin tiempo 🕑

    if orientjson:
        data = bills_data.to_json(orient=orientjson)
    else:
        data = bills_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[Bills]")

@services.opt_return(type="[[[string, string], [number, ...]], ...]")
def analysis(value: dict[str, Index | MultiIndex]):
    """Devolucion de informacion sobre Bills, donde las llaves strings y los valores
    son los indices de las filas con errores."""
    return ServiceResult({
        "data": [[k, v.to_list()] for k, v in value.items()],
        "type": "[string, [number, ...]]"
    })

@services.opt_return(type="[string|None, string|None, string|None, *[string, ...]]")
def exceptions(value: tuple[str | None, str | None, str | None, *tuple[str, ...]]):
    """Devolucion de informacion sobre los mensajes de errores encontrados en la data Bills."""
    errs = list(f"{type(e).__name__}: {e}" if isinstance(e, Exception) else None for e in value)
    return ServiceResult({
        "data": errs,
        "type": "[string|None, string|None, string|None, ...[string, ...]]"
    })
