"""Modulo para definir parametros generales de los servicios."""

from uuid import UUID
from .types import ServiceOptParameter, ServiceOptReturn, ServiceResult
from .operation import _return_default, return_default

def _return_none(_):
    return _return_default(_)

return_none = return_default

def _param_key_uuid(value):
    if isinstance(value, str) and value:
        try:
            return UUID(value)
        except ValueError:
            pass
    raise TypeError("el valor debe ser de tipo string[UUID].")

param_key_uuid = ServiceOptParameter(name="key_uuid", type="string[UUID]", func=_param_key_uuid)

def _return_uuid(value: UUID) -> ServiceResult:
    return {
        "data": str(value),
        "type": "UUID"
    }

return_uuid = ServiceOptReturn(
    name="return",
    type="{'data': string, 'type': string}",
    func=_return_uuid
)

def _return_list_uuid(value: list[UUID]) -> ServiceResult:
    return {
        "data": [str(item) for item in value],
        "type": "[UUID, ...]"
    }

return_list_uuid = ServiceOptReturn(
    name="return",
    type="{'data': [string, ...], 'type': string}, ...",
    func=_return_list_uuid
)
