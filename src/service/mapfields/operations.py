"""Modulo para manejar las operaciones comunes del servicio de MapFields."""

from uuid import UUID
from db.datastore import DataStore
from core.mapfields import MapFields
from service.decorator import services
from service.mapfields import params, returns
import service.common as c

@services.operation(params.mapfields, c.returns.uuid, dataid=params.dataid)
def create(value: list[tuple[str, str]], /, idstore: UUID, dataid: UUID = None):
    """Crea un nuevo mapeo de campos."""
    datastore = DataStore.get_datastore(idstore)

    if not value:
        raise ValueError("no hay valores para hacer el mapeo de campo.")

    mapfields = MapFields(*value)
    uuid = datastore.append(mapfields)
    if dataid:
        mapfields = datastore.pop(uuid)
        datastore[dataid] = mapfields
    else:
        dataid = uuid
    return dataid

@services.operation(c.params.index, c.returns.uuids)
def getall(index: slice | None, /, idstore: UUID):
    """Obtener todos los IDs de mapeo de campos."""
    datastore = DataStore.get_datastore(idstore)

    if index is None:
        index = slice(None, None)
    return list(datastore.keys())[index]

@services.operation(params.dataid, returns.mapfields)
def get(key: UUID, /, idstore: UUID):
    """Obtener el mapeo de campos (MapFields) con el ID."""
    datastore = DataStore.get_datastore(idstore)

    if key in datastore:
        return datastore[key]
    raise KeyError(f"no se encuentra el MapFields con la llave UUID: {key}")

@services.operation(c.params.optional(params.dataid), c.returns.exitstatus)
def pop(dataid: UUID | None, /, idstore: UUID):
    """Elimina un mapfields segun el identificador, sin este se elimina el ultimo."""
    datastore = DataStore.get_datastore(idstore)

    if dataid is None:
        list_dataid = getall(slice(-1, None), idstore=idstore)
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    if dataid in datastore:
        datastore.pop(dataid)
    if dataid in datastore.persistent:
        datastore.persistent.remove(dataid)
    return 0

@services.operation(params.dataid, c.returns.exitstatus)
def persistent(dataid: UUID, /, idstore: UUID):
    """Agregar el ID de los datos a los persistentes."""
    datastore = DataStore.get_datastore(idstore)

    if dataid not in datastore.persistent:
        datastore.persistent.append(dataid)
    else:
        datastore.persistent.remove(dataid)
    return 0
