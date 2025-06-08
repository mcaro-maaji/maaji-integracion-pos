"""Modulo para definir devoluciones generales de los servicios."""

from uuid import UUID
from service.types import ServiceResult
from service.decorator import services

@services.opt_return(type="None")
def none(_):
    """Devolucion de servicio con valor None."""
    return ServiceResult({
        "data": None,
        "type": "None"
    })

@services.opt_return(type="string[UUID]")
def uuid(value: UUID):
    """Devolucion de servicio con valor de un string UUID."""
    return ServiceResult({
        "data": str(value),
        "type": "string[UUID]"
    })

@services.opt_return(type="[string[UUID], ...]")
def uuids(value: list[UUID]):
    """Devolucion de servicio con valor de un listado de string UUID."""
    return ServiceResult({
        "data": [str(item) for item in value],
        "type": "[string[UUID], ...]"
    })
