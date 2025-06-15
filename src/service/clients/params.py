"""Modulo para definir parametros del servicio de clients: core.clients"""

from typing import Literal
from uuid import UUID
from service.decorator import services
import service.common as c
import service.mapfields as m

@services.parameter(type="'cegid' | 'shopify'")
def pos(value: str) -> Literal["cegid", "shopify"]:
    """Parametro para elegir el POS que se usara en la operacion."""
    value = str(value).lower()

    if value in ["cegid", "shopify"]:
        return value
    raise ValueError("se debe elegir el alguno de estos valores: 'cegid' | 'shopify'")

@services.parameter(type="ClientsPOS[UUID]")
def dataid(value: str | UUID):
    """Parametro para contiene el ID de los campos de los clientes."""
    return c.params.uuid(value)

@services.parameter(type="boolean")
def converted(value: bool = False):
    """Parametro para escoger si data de clientes son los convertidos o no por MapFields."""
    return c.params.boolean(value)

@services.parameter(type="boolean")
def force(value: bool = False):
    """Parametro para forzar la creacion de los datos de los clientes, hace espacio en memoria."""
    return c.params.boolean(value)

@services.parameter(type="string[] | number[]")
def indices(value: list[str] | list[int]):
    """Parametro que verifica que el valor es tipo ArrayList con valores tipo string o number."""
    value = c.params.arraylist(value)
    contain_str_or_int = all(isinstance(i, (str, int)) for i in value)
    if contain_str_or_int:
        return value
    raise TypeError("el valor indices debe contener valores tipo string o number.")

@services.parameter(type="[[[string, string], [object, ...]], ...]")
def dataupdate(value: list[tuple[tuple[str, str], list[object]]]):
    """Parametro que verifica que sea un mapping con llaves MapFields y un listado de datos."""
    value = c.params.arraylist(value)
    try:
        return {m.params.mapfield(tuple(k)): c.params.arraylist(v) for k, v in value}
    except ValueError:
        pass
    raise TypeError("el contenido del valor debe ser de tipo [[string, string]: [object, ...]]")

@services.parameter(type="[[[string, string], [number, ...]], ...]")
def analysis(value: list[tuple[tuple[str, str], list[int]]]):
    """Parametro de informacion sobre ClientesPOS, donde las llaves son el MapField y los valores
    son los indices de las filas con errores."""
    content = dataupdate(value)
    for i in content.values():
        indices(i)
    return content
