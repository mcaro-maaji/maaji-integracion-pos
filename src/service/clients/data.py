"""Modulo para gestionar los datos en cache de los clientes."""

from uuid import UUID
from core.clients import ClientsPOS as _ClientsPOS, ClientsCegid, ClientsShopify
from utils.datastore import DataStore
from utils.typing import FilePath, ReadBuffer, ReadCsvBuffer
import service.mapfields.clients as mapfields_clients

DS_CLIENTS_POS: DataStore[_ClientsPOS] = DataStore(
    max_length=5,                         # 5 sitios disponibles para crear data Clients.
    max_size=20 * 1e6,                    # 20 Megabytes.
    # max_duration=timedelta(hours=1)     # 12 minutos cada item, total de 60 minutos.
)

def ds_clients_pos_calc_size(clients: _ClientsPOS):
    """Callback para calcular el tamaño de los datos de los clientes."""
    size = int(clients.data_pos.memory_usage(deep=True).sum())
    size += int(clients.data.memory_usage(deep=True).sum())
    return size

DS_CLIENTS_POS.calc_size = ds_clients_pos_calc_size

def create(fpath_or_buffer: FilePath | ReadBuffer | ReadCsvBuffer,
           /,
           pos: str = "cegid",
           ftype: str = "csv",
           delimeter: str = "|",
           encoding: str = "utf-8",
           idmapfields: UUID = None):
    """Crea una instancia de ClientsPOS y la guarda en un DataStore, devuelve el ID."""

    if pos == "cegid":
        ClientsPOS = ClientsCegid
        default_idmapfields = mapfields_clients.getall()[0]
    elif pos == "shopify":
        ClientsPOS = ClientsShopify
        default_idmapfields = mapfields_clients.getall()[1]
    else:
        raise ValueError("no se ha seleccionado un POS valido.")

    if idmapfields is None:
        idmapfields = default_idmapfields

    mapfields = mapfields_clients.get(idmapfields)
    data = ClientsPOS(
        fpath_or_buffer,
        ftype=ftype,
        delimiter=delimeter,
        encoding=encoding,
        mapfields=mapfields
    )

    uuid = DS_CLIENTS_POS.append(data)
    return uuid
