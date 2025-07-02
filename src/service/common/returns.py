"""Modulo para definir devoluciones generales de los servicios."""

from uuid import UUID
from quart import Response
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

@services.opt_return(type="string[ExitStatus]")
def exitstatus(value: int | str | tuple[int, str]):
    """Devolucion de servicio que indica el estado devuelto de la operacion con un numero."""
    if isinstance(value, (int, str)):
        status = str(value)
    elif isinstance(value, tuple) and len(value) == 2:
        num, msg = value
        status = f"code: {num} | message: '{msg}'"
    else:
        status = str(int(not bool(value)))
    return ServiceResult({
        "data": status,
        "type": "string[ExitStatus]"
    })

@services.opt_return(type="string[]")
def fields(value: list[str]):
    """Devolucion de servicio con valor de los campos."""
    return ServiceResult({
        "data": value,
        "type": "string[]"
    })

@services.opt_return(type="[[string, string], ...]")
def mapfields(value: list[tuple[str, str]]):
    """Devolucion de servicio con valor de MapFields."""
    return ServiceResult({
        "data": value,
        "type": "[[string, string], ...]"
    })

@services.opt_return(type="object")
def response(value: Response):
    """Devolucion de servicio con una respuesta a una peticion HTTP."""
    if not isinstance(value, Response):
        raise TypeError("el valor debe ser de tipo Response")
    return ServiceResult({
        "data": value,
        "type": "[[string, string], ...]"
    })
