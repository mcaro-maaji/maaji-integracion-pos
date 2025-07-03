"""Modulo para definir devoluciones del servicio de productos: core.products"""

from pandas import Index, MultiIndex
from core.products import Products
from service.types import ServiceResult
from service.decorator import services
from service.common.params import JsonFrameOrient

@services.opt_return(type="JsonOriented[Products]")
def datajson(value: tuple[Products, bool, JsonFrameOrient]):
    """Devolucion de los datos de los clientes."""
    products, fixed, orientjson = value

    if not isinstance(products, Products):
        raise TypeError("el valor devuelto por la operacion debe ser de tipo Products.")

    products_data = products.data if fixed else products.data # 😅 me quede sin tiempo 🕑

    if orientjson:
        data = products_data.to_json(orient=orientjson)
    else:
        data = products_data.to_dict("records")

    return ServiceResult(data=data, type="JsonOriented[Products]")

@services.opt_return(type="[[[string, string], [number, ...]], ...]")
def analysis(value: dict[str, Index | MultiIndex]):
    """Devolucion de informacion sobre Products, donde las llaves strings y los valores
    son los indices de las filas con errores."""
    return ServiceResult({
        "data": [[k, v.to_list()] for k, v in value.items()],
        "type": "[string, [number, ...]]"
    })

@services.opt_return(type="[string|None, string|None, string|None, *[string, ...]]")
def exceptions(value: tuple[str | None, str | None, str | None, *tuple[str, ...]]):
    """Devolucion de informacion sobre los mensajes de errores encontrados en la data Products."""
    errs = list(f"{type(e).__name__}: {e}" if isinstance(e, Exception) else None for e in value)
    return ServiceResult({
        "data": errs,
        "type": "[string|None, string|None, string|None, ...[string, ...]]"
    })
