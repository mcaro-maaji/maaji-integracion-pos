"""Modulo para definir parametros del servicio de MapFields: utils.mapfields"""

from uuid import UUID
from service.decorator import services
from service import common

@services.parameter(type="MapFields[UUID]")
def dataid(value: str | UUID):
    """Parametro para contiene el ID del mapeo de campos de los clientes."""
    return common.params.uuid(value)

@services.parameter(type="[string, string]")
def mapfield(value: tuple[str, str]):
    """Parametro que valida que el valor sea un tipo MapFields."""
    value = tuple(common.params.fields(value))
    if len(value) != 2:
        raise ValueError("el valor de ser un mapfield que contiene 2 elementos de tipo string.")
    return value

@services.parameter(type="[[string, string], ...]")
def mapfields(value: list[tuple[str, str]]):
    """Parametro que valida que el valor sea un listado de MapFields."""
    value = common.params.arraylist(value)
    return [mapfield(i) for i in value]
