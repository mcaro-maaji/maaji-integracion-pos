"""Modulo para disponer de todos los recursos a la web a modo de servicio de los clientes."""

from uuid import UUID
from service import services
import service.clients.cegid as clients

def _generate_dataid(init: UUID = None):
    """Obtener el ID de los datos clientesPOS"""
    _dataid: UUID | None = init

    def get_dataid(value: UUID = None):
        nonlocal _dataid

        if not value is None:
            _dataid = value
        if _dataid is None:
            raise ValueError("no se ha creado un set de datos ClientesPOS para leer.")
        return _dataid

    return get_dataid

dataid = _generate_dataid()

@services.operation(
    clients.create.opt_return,
    *clients.create.parameters,
    pos=clients.params.pos,
    **clients.create.parameterskv,
)
async def datafromfile(**kwargs):
    """Crea los datos de los clientes."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    kwargs["dataid"] = kwargs.pop("dataid", None) or _dataid
    kwargs["datafrom"] = "file"
    kwargs["force"] = True

    key = "payload.web.files"
    uuid = await clients.create(key, **kwargs)

    if uuid not in clients.data.DS_CLIENTS_POS.persistent:
        clients.persistent(uuid) # append new uuid
        if not _dataid is None:
            clients.persistent(dataid) # remove old uuid

    return dataid(uuid)

@services.operation(clients.returns.datajson, converted=clients.params.converted)
def getdata(*, converted=False):
    """Obtiene los datos de los clientes."""
    [data, *_] = clients.get(dataid())
    return data, converted, "records"

@services.operation(clients.fullfix.opt_return)
def fullfix():
    """Obtiene los datos de los clientes."""
    return clients.fullfix(dataid())

service = services.service("clients", datafromfile, getdata, fullfix)
