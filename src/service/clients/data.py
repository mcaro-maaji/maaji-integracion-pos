"""Modulo para gestionar los datos en cache de los clientes."""

from uuid import UUID
from io import BytesIO
from pathlib import Path
from core.clients import ClientsPOS, ClientsCegid, ClientsShopify
from utils.datastore import DataStore
from service.types import Service
from service.operation import ServiceOperation
from service.params import return_uuid, return_list_uuid
from service.mapfields.clients import (
    _opt_getall as mapfields_getall,
    _opt_get as mapfields_get
)
from .params import (
    param_pos,
    param_fpath,
    param_raw,
    param_ftype,
    param_delimeter,
    param_encoding,
    param_uuid_mapfields,
    param_uuid_data,
    param_from_pos,
    return_clients_data
)

CLIENTS_DATASTORE: DataStore[ClientsPOS] = DataStore(
    max_length=5,                         # 5 sitios disponibles para crear data Clients.
    max_size=10 * 1e6,                    # 10 Megabytes.
    # max_duration=timedelta(hours=1)     # 12 minutos cada item, total de 60 minutos.
)

def clients_datastore_calc_size(clients: ClientsPOS):
    """Callback para calcular el tamaño de los datos de los clientes."""
    size = int(clients.data_pos.memory_usage(deep=True).sum())
    size += int(clients.data.memory_usage(deep=True).sum())
    return size

CLIENTS_DATASTORE.calc_size = clients_datastore_calc_size

def _opt_create(fpath_or_buffer: Path | BytesIO,
                /,
                pos: str = "cegid",
                ftype: str = "csv",
                delimeter: str = "|",
                encoding: str = "utf-8",
                uuid_mapfields: UUID = None):

    if pos == "shopify":
        uuid_mf_default = mapfields_getall()[1]
        AliasClientsPOS = ClientsShopify
    else:
        uuid_mf_default = mapfields_getall()[0]
        AliasClientsPOS = ClientsCegid

    if uuid_mapfields is None:
        uuid_mapfields = uuid_mf_default

    mapfields = mapfields_get(uuid_mapfields)
    data = AliasClientsPOS(
        fpath_or_buffer,
        ftype=ftype,
        delimiter=delimeter,
        encoding=encoding,
        mapfields=mapfields
    )
    uuid = CLIENTS_DATASTORE.append(data)
    return uuid

params_fromraw = {
    "parameters": [param_raw],
    "parameters_kv": {
        "pos": param_pos,
        "ftype": param_ftype,
        "delimeter": param_delimeter,
        "encoding": param_encoding,
        "uuid_mapfields": param_uuid_mapfields
    },
    "return": return_uuid
}

def _opt_fromraw(raw: str,
                 /,
                 pos: str = "cegid",
                 ftype: str = "csv",
                 delimeter: str = "|",
                 encoding: str = "utf-8",
                 uuid_mapfields: UUID = None):

    raw_bytes = raw.encode(encoding)
    buffer = BytesIO(raw_bytes)
    uuid = _opt_create(
        buffer,
        pos=pos,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        uuid_mapfields=uuid_mapfields
    )
    return uuid

opt_fromraw = ServiceOperation(name="fromraw", func=_opt_fromraw, **params_fromraw)

params_fromfile = {
    "parameters": [param_fpath],
    "parameters_kv": {
        "pos": param_pos,
        "ftype": param_ftype,
        "delimeter": param_delimeter,
        "encoding": param_encoding,
        "uuid_mapfields": param_uuid_mapfields
    },
    "return": return_uuid
}

def _opt_fromfile(fpath: Path,
                  /,
                  pos: str = "cegid",
                  ftype: str = "csv",
                  delimeter: str = "|",
                  encoding: str = "utf-8",
                  uuid_mapfields: UUID = None):

    uuid = _opt_create(
        fpath,
        pos=pos,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        uuid_mapfields=uuid_mapfields
    )
    return uuid

opt_fromfile = ServiceOperation(name="fromfile", func=_opt_fromfile, **params_fromfile)

params_getall = {
    "parameters": [],
    "return": return_list_uuid
}

def _opt_getall():
    return list(CLIENTS_DATASTORE.keys())

opt_getall = ServiceOperation(name="getall", func=_opt_getall, **params_getall)

params_get = {
    "parameters": [param_uuid_data],
    "parameters_kv": {
        "from_pos": param_from_pos
    },
    "return": return_clients_data
}

def _opt_get(uuid_clients: UUID, /, from_pos: bool = True):
    try:
        clients = CLIENTS_DATASTORE[uuid_clients]
    except KeyError as err:
        msg = "No se ha encontrado los datos de los clientes con el UUID proporcionado."
        raise KeyError(msg) from err

    if from_pos:
        return clients.data_pos.to_dict("split")
    return clients.data.to_dict("split")

opt_get = ServiceOperation(name="get", func=_opt_get, **params_get)

operations = [
    opt_fromraw,
    opt_fromfile,
    opt_getall,
    opt_get
]

service = Service(name="clients_data", operations=operations)
