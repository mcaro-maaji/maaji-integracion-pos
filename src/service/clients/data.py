"""Modulo para gestionar los datos en cache de los clientes."""

from uuid import UUID
from datetime import timedelta
from quart import has_request_context, request
from quart.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError, InternalServerError
from data.store import DataStore
from data.io import DataIO, SupportDataIO, ModeDataIO
from service import mapfields
from core.clients import (
    ClientsPOS as _ClientsPOS,
    ClientsCegid,
    ClientsShopify,
    MAPFIELDS_CLIENTS_POS_CEGID,
    MAPFIELDS_CLIENTS_POS_SHOPIFY
)

DS_CLIENTS_POS: DataStore[_ClientsPOS[str]] = DataStore(
    max_length=7,                         # 7 sitios disponibles para crear data Clients.
    max_size=35 * 1e6,                    # 35 Megabytes.
    max_duration=timedelta(minutes=70)    # 10 minutos cada item
)

def ds_clients_pos_calc_size(clients: _ClientsPOS[str]):
    """Callback para calcular el tamaño de los datos de los clientes."""
    size = int(clients.data_pos.memory_usage(deep=True).sum())
    size += int(clients.data.memory_usage(deep=True).sum())
    return size

DS_CLIENTS_POS.calc_size = ds_clients_pos_calc_size

async def source_from_request(source: DataIO, mode: ModeDataIO):
    """Obtiene un fileio desde un contexto de request."""
    if mode == "request":
        if not has_request_context():
            raise InternalServerError("no hay contexto de un request HTTP")

        payload = "payload.files"
        if isinstance(source, str):
            payload = source

        source: FileStorage = (await request.files).get(payload)

        if not source:
            msg = "no se ha encontrado el archivo en la peticion con paylaod/key: " + payload
            raise BadRequestKeyError(msg)

    return source

async def create(*,
                 source: DataIO = None,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 pos: str = "cegid",
                 dataid: UUID = None,
                 force: bool = False,
                 idmapfields: UUID = None,
                 **kwargs: ...):
    """Crea una instancia de ClientsPOS y la guarda en un DataStore, devuelve el ID."""

    if pos == "cegid":
        ClientsPOS = ClientsCegid
        default_mapfields = MAPFIELDS_CLIENTS_POS_CEGID
    elif pos == "shopify":
        ClientsPOS = ClientsShopify
        default_mapfields = MAPFIELDS_CLIENTS_POS_SHOPIFY
    else:
        raise ValueError("no se ha seleccionado un POS valido.")

    if not idmapfields is None:
        value_mapfields = mapfields.clients.get(idmapfields)
    else:
        value_mapfields = default_mapfields

    source = await source_from_request(source, mode)

    data = ClientsPOS(
        value_mapfields,
        source=source,
        support=support,
        mode=mode,
        **kwargs
    )

    if not isinstance(dataid, UUID) and not dataid is None:
        raise TypeError("el parametro dataid debe ser de tipo string[UUID]")

    uuid = DS_CLIENTS_POS.append(data, force=force)
    if dataid:
        clients = DS_CLIENTS_POS.pop(uuid)
        DS_CLIENTS_POS[dataid] = clients
    else:
        dataid = uuid
    return dataid
