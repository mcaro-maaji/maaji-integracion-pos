"""Modulo para definir devoluciones del servicio de interfaz contable: core.afi"""

from pandas import Index, MultiIndex
from core.afi import AFI
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[AFI]")
def datajson(value: tuple[AFI, bool, JsonFrameOrient]):
    """Devolucion de los datos de la interfaz contable."""
    afi, fixed, orientjson = value

    if not isinstance(afi, AFI):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo AFI.")

    afi_data = afi.data if fixed else afi.data_src

    if orientjson:
        data = afi_data.to_json(orient=orientjson)
    else:
        data = afi_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[AFI]")

@services.opt_return(type="[[[string, string], [number, ...]], ...]")
def analysis(value: dict[tuple[str, str], Index | MultiIndex]):
    """Devolucion de informacion sobre AFI, donde las llaves son el MapField y los valores
    son los indices de las filas con errores."""
    return ServiceResult({
        "data": [[k, v.to_list()] for k, v in value.items()],
        "type": "[[string, string], [number, ...]]"
    })

@services.opt_return(type="[string|None, string|None, string|None, *[string, ...]]")
def exceptions(value: tuple[str | None, str | None, str | None, *tuple[str, ...]]):
    """Devolucion de informacion sobre los mensajes de errores encontrados en la data AFI."""
    errs = list(f"{type(e).__name__}: {e}" if isinstance(e, Exception) else None for e in value)
    return ServiceResult({
        "data": errs,
        "type": "[string|None, string|None, string|None, ...[string, ...]]"
    })
