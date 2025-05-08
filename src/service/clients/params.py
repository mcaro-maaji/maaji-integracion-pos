"""Modulo para definir parametros del servicio de clients: core.clients"""

from codecs import lookup as codecs_lookup
from pathlib import Path
from service.types import (
    ServiceOptParameter,
    ServiceOptReturn,
    ServiceResult
)
from service.params import _param_key_uuid

def _param_pos(value):
    if value in ["cegid", "shopify"]:
        return value
    raise ValueError("se debe elegir el alguno de estos POS: ['cegid' | 'shopify'].")

param_pos = ServiceOptParameter(name="pos", type="['cegid' | 'shopify']", func=_param_pos)

def _param_fpath(value):
    if isinstance(value, str) and value:
        path = Path(value)
        if path.is_file():
            return path
        raise FileNotFoundError(f"archivo no encontrado en la ruta: {value}")
    raise TypeError("el valor debe ser de tipo 'string' y no vacio.")

param_fpath = ServiceOptParameter(name="fpath", type="string", func=_param_fpath)

def _param_raw(value):
    if isinstance(value, str) and value:
        return value
    raise TypeError("el valor debe ser de tipo 'string' y no vacio.")

param_raw = ServiceOptParameter(name="raw", type="string", func=_param_raw)

def _param_ftype(value):
    if value in ["csv", "excel", "json"]:
        return value
    raise ValueError("se debe elegir el alguno de estos ftype: ['csv' | 'excel' | 'json'].")

param_ftype = ServiceOptParameter(
    name="ftype",
    type="['csv' | 'excel' | 'json']",
    func=_param_ftype
)

def _param_delimeter(value):
    if isinstance(value, str) and value:
        return value
    raise TypeError("el valor debe ser de tipo 'string' y no vacio.")

param_delimeter = ServiceOptParameter(name="delimeter", type="string", func=_param_delimeter)

def _param_encoding(value):
    if isinstance(value, str) and value:
        try:
            codecs_lookup(value)
            return value
        except LookupError as err:
            raise LookupError(f"encoding no valido: {value}") from err
    raise TypeError("el valor debe ser de tipo 'string' y no vacio.")

param_encoding = ServiceOptParameter(name="encoding", type="string", func=_param_encoding)

param_uuid_mapfields = ServiceOptParameter(
    name="uuid_mapfields",
    type="string[UUID]",
    func=_param_key_uuid
)

param_uuid_data = ServiceOptParameter(
    name="uuid_data",
    type="string[UUID]",
    func=_param_key_uuid
)

def _param_from_pos(value):
    if isinstance(value, bool):
        return value
    return False

param_from_pos = ServiceOptParameter(name="from_pos", type="boolean", func=_param_from_pos)

def _return_clients_data(value: dict) -> ServiceResult:
    return {
        "data": value,
        "type": "ClientsPOS"
    }

return_clients_data = ServiceOptReturn(
    name="return",
    type="""
    {
        'index': ['row1', 'row2', ...],
        'columns': ['col1', 'col2', ...],
        'data': [[string, string], [string, string], ...]
    }
    """,
    func=_return_clients_data
)
