"""Modulo para tener un servicio MapField de los datos ClientsPOS."""

from uuid import UUID
from datetime import timedelta
from core.clients import MAPFIELDS_POS_CEGID, MAPFIELDS_POS_SHOPIFY_MX
from core.mapfields import MapFields
from db.datastore import DataStore
from service.decorator import services
from service.mapfields import operations as opt

DS_MAPFIELDS_CLIENTS: DataStore[MapFields] = DataStore(
    max_length=7,                         # 5 sitios disponibles y 2 por defecto.
    max_size=1,                           # 1 slot, sin calculos
    max_duration=timedelta(minutes=70)    # 10 minutos cada item
)

default_mapfields = DS_MAPFIELDS_CLIENTS.extend(MAPFIELDS_POS_CEGID, MAPFIELDS_POS_SHOPIFY_MX)
DS_MAPFIELDS_CLIENTS.persistent.extend(default_mapfields)

@services.operation(opt.create.opt_return, *opt.create.parameters, **opt.create.parameterskv)
def create(value: list[tuple[str, str]], /, dataid: UUID = None):
    """Crea un nuevo mapeo de campos de los ClientesPOS."""
    return opt.create(value, dataid=dataid, idstore=DS_MAPFIELDS_CLIENTS.id)

@services.operation(opt.getall.opt_return, *opt.getall.parameters, **opt.getall.parameterskv)
def getall(index: slice = None):
    """Obtener todos los IDs de mapeo de campos (MapFields) de los clientes."""
    return opt.getall(index, idstore=DS_MAPFIELDS_CLIENTS.id)

@services.operation(opt.get.opt_return, *opt.get.parameters, **opt.get.parameterskv)
def get(key: UUID):
    """Obtener el mapeo de campos (MapFields) de los clientes con el ID."""
    return opt.get(key, idstore=DS_MAPFIELDS_CLIENTS.id)

@services.operation(opt.pop.opt_return, *opt.pop.parameters, **opt.pop.parameterskv)
def pop(dataid: UUID | None):
    """Elimina un mapfields segun el identificador, sin este se elimina el ultimo."""
    return opt.pop(dataid, idstore=DS_MAPFIELDS_CLIENTS.id)

@services.operation(
    opt.persistent.opt_return,
    *opt.persistent.parameters,
    **opt.persistent.parameterskv
)
def persistent(dataid: UUID):
    """Agregar el ID de los datos a los persistentes."""
    return opt.persistent(dataid, idstore=DS_MAPFIELDS_CLIENTS.id)

service_clients = services.service("clients", create, getall, get, pop, persistent)
