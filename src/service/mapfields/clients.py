"""Modulo para tener un servicio MapField de los datos clientes."""

from datetime import timedelta
from uuid import UUID
from core.clients import MAPFIELDS_POS_CEGID, MAPFIELDS_POS_SHOPIFY_MX
from utils.datastore import DataStore
from service.types import Service
from service.operation import ServiceOperation
from service.params import param_key_uuid, return_list_uuid
from .params import return_mapfields

CLIENTS_MAPFIELDS = DataStore(
    MAPFIELDS_POS_CEGID,
    MAPFIELDS_POS_SHOPIFY_MX,
    maxitems=12, # 10 sitios disponibles para crear MapFields
    maxsize=1,
    maxtime=timedelta(days=365*5)
)

def _opt_getall():
    return list(CLIENTS_MAPFIELDS.keys())

params_getall = {
    "parameters": [],
    "return": return_list_uuid
}

opt_getall = ServiceOperation(name="getall", func=_opt_getall, **params_getall)

def _opt_get(key: UUID):
    if key in CLIENTS_MAPFIELDS:
        return CLIENTS_MAPFIELDS[key]
    raise KeyError(f"No se encuentra el MapFields de Clientes con la llave UUID: {key}")

params_get = {
    "parameters": [param_key_uuid],
    "return": return_mapfields
}

opt_get = ServiceOperation(name="get", func=_opt_get, **params_get)

operations = [
    opt_getall,
    opt_get
]

service = Service(name="mapfields_clients", operations=operations)
