"""Modulo para definir parametros del servicio de MapFields."""

from typing import TypedDict, NotRequired, TypeGuard
from utils.mapfields import MapFields, MapFieldFunc
from utils.typing import NonStringIterable, is_dict_str
from service.types import ServiceOptReturn, ServiceResult

def _return_mapfields(value: MapFields) -> ServiceResult:
    return {
        "data": value,
        "type": "MapFields[string, ClientField]"
    }

return_mapfields = ServiceOptReturn(
    name="return",
    type="{'data': [[string, string], ...], 'type': string}",
    func=_return_mapfields
)

# TODO: servicio de creacion mapfields
class MapFieldParam(TypedDict):
    """Parametro para mapear los campos de los clientes, ej:
    
    JSON
    
    >>> {
    >>>     "mapfield": ["field 1", "mapfield 1"],  // tuple[str, str]
    >>>     "mapfunc": "equal"                      // NotRequired[MapFieldFunc]
    >>>     "mapdata": {                            // NotRequired[dict[str, str]]
    >>>        "value expected": "value mapped"
    >>>    }
    >>> }
    """
    mapfield: tuple[str, str]
    mapfunc: NotRequired[MapFieldFunc]
    mapdata: NotRequired[dict[str, str]]

def is_mapfieldparam(value) -> TypeGuard[MapFieldParam]:
    """Comprueba que un elemento es de tipo MapFieldParam."""

    if not isinstance(value, dict):
        return False
    has_mapfield = "mapfield" in value and isinstance(value['mapfield'], NonStringIterable)
    has_mapfield = has_mapfield and len(value['mapfield']) == 2
    has_mapfunc = "mapfunc" in value and value in MapFieldFunc or "mapfunc" not in value
    has_mapdata = "mapdata" in value and is_dict_str(value["mapdata"]) or "mapdata" not in value
    return has_mapfield and has_mapfunc and has_mapdata
