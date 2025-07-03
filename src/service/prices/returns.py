"""Modulo para definir devoluciones del servicio de prices: core.prices"""

from pandas import Index, MultiIndex
from core.prices import Prices
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[Prices]")
def datajson(value: tuple[Prices, bool, JsonFrameOrient]):
    """Devolucion de los datos de los precios."""
    prices, fixed, orientjson = value

    if not isinstance(prices, Prices):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo Prices.")

    prices_data = prices.data if fixed else prices.data # 😅 me quede sin tiempo 🕑

    if orientjson:
        data = prices_data.to_json(orient=orientjson)
    else:
        data = prices_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[Prices]")

@services.opt_return(type="[[[string, string], [number, ...]], ...]")
def analysis(value: dict[str, Index | MultiIndex]):
    """Devolucion de informacion sobre Prices, donde las llaves strings y los valores
    son los indices de las filas con errores."""
    return ServiceResult({
        "data": [[k, v.to_list()] for k, v in value.items()],
        "type": "[string, [number, ...]]"
    })

@services.opt_return(type="[string|None, string|None, string|None, *[string, ...]]")
def exceptions(value: tuple[str | None, str | None, str | None, *tuple[str, ...]]):
    """Devolucion de informacion sobre los mensajes de errores encontrados en la data Prices."""
    errs = list(f"{type(e).__name__}: {e}" if isinstance(e, Exception) else None for e in value)
    return ServiceResult({
        "data": errs,
        "type": "[string|None, string|None, string|None, ...[string, ...]]"
    })
