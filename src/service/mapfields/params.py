"""Modulo para definir parametros del servicio de MapFields: utils.mapfields"""

from uuid import UUID
from service.decorator import services
from service.common import params

@services.parameter(type="MapFields[UUID]")
def idmapfields(value: str | UUID):
    """Parametro para contiene el ID del mapeo de campos de los clientes."""
    return params.uuid(value)

@services.parameter(type="string[]")
def fields(value: list[str]):
    """Parametro que verifica que el valor es de tipo ArrayList con valores tipo string"""
    value = params.arraylist(value)
    contain_str = all(isinstance(i, str) for i in value)
    if contain_str:
        return value
    raise TypeError("el valor arraylist debe contener valores tipo string.")

@services.parameter(type="[string, string]")
def mapfield(value: tuple[str, str]):
    """Parametro que valida que el valor sea un tipo MapFields."""
    value = fields(value)
    if len(value) != 2:
        raise ValueError("el valor de ser un mapfield que contiene 2 elementos de tipo string.")
    return value

@services.parameter(type="[[string, string], ...]")
def mapfields(value: list[tuple[str, str]]):
    """Parametro que valida que el valor sea un listado de MapFields."""
    value = params.arraylist(value)
    return [mapfield(i) for i in value]
