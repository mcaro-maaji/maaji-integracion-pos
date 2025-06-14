"""Modulo para gestionar los datos en cache de los clientes."""

from uuid import UUID
from datetime import timedelta
from db.datastore import DataStore
from utils.typing import FilePath, ReadBuffer, ReadCsvBuffer
from core.clients import (
    ClientsPOS as _ClientsPOS,
    ClientsCegid,
    ClientsShopify,
    MAPFIELDS_POS_CEGID,
    MAPFIELDS_POS_SHOPIFY_MX
)
import service.mapfields as m

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

def create(fpath_or_buffer: FilePath | ReadBuffer | ReadCsvBuffer,
           /,
           pos: str = "cegid",
           dataid: UUID = None,
           ftype: str = "csv",
           delimeter: str = "|",
           encoding: str = "utf-8",
           idmapfields: UUID = None,
           force: bool = False):
    """Crea una instancia de ClientsPOS y la guarda en un DataStore, devuelve el ID."""

    if pos == "cegid":
        ClientsPOS = ClientsCegid
        default_mapfields = MAPFIELDS_POS_CEGID
    elif pos == "shopify":
        ClientsPOS = ClientsShopify
        default_mapfields = MAPFIELDS_POS_SHOPIFY_MX
    else:
        raise ValueError("no se ha seleccionado un POS valido.")

    if not idmapfields is None:
        mapfields = m.clients.get(idmapfields)
    else:
        mapfields = default_mapfields

    data = ClientsPOS(
        fpath_or_buffer,
        ftype=ftype,
        delimiter=delimeter,
        encoding=encoding,
        mapfields=mapfields
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
