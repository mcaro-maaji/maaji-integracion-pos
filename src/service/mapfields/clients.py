"""Modulo para tener un servicio MapField de los datos ClientsPOS."""

from uuid import UUID
from datetime import timedelta
from core.clients import MAPFIELDS_POS_CEGID, MAPFIELDS_POS_SHOPIFY_MX
from utils.mapfields import MapFields
from utils.datastore import DataStore
from service import common as c
from service.decorator import services
from service.mapfields import params, returns

DS_MAPFIELDS_CLIENTS: DataStore[MapFields] = DataStore(
    max_length=7, # 5 sitios disponibles para crear MapFields y 2 por defecto.
    max_size=1,
    max_duration=timedelta(days=365*5)
)

DS_MAPFIELDS_CLIENTS.extend(MAPFIELDS_POS_CEGID, MAPFIELDS_POS_SHOPIFY_MX)

@services.operation(c.params.index, c.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de mapeo de campos (MapFields) de los clientes."""
    if index is None:
        index = slice(None, None)
    return list(DS_MAPFIELDS_CLIENTS.keys())[index]

@services.operation(params.idmapfields, returns.mapfields)
def get(key: UUID):
    """Obtener el mapeo de campos (MapFields) de los clientes con el ID."""

    if key in DS_MAPFIELDS_CLIENTS:
        return DS_MAPFIELDS_CLIENTS[key]
    raise KeyError(f"no se encuentra el MapFields de Clientes con la llave UUID: '{key}'")

service_clients = services.service("clients", getall, get)
