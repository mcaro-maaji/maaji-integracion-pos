"""Modulo para definir devoluciones generales de los servicios."""

from uuid import UUID
from service.types import ServiceResult
from service.decorator import services
from service.operation import opt_return_default as _default

@services.opt_return(type="type[object]")
def default(value: object):
    """Devolucion de servicio con el valor dado por la ejecucion de la operacion."""
    return _default(value)

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

@services.opt_return(type="ExitStatus[number]")
def exitstatus(value: int):
    """Devolucion de servicio que indica el estado devuelto de la operacion con un numero."""
    if isinstance(value, int):
        status = value
    else:
        status = int(not bool(value))
    return ServiceResult({
        "data": status,
        "type": "ExitStatus[number]"
    })
