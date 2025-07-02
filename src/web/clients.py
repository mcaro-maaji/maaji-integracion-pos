"""Modulo para disponer de todos los recursos a la web a modo de servicio de los clientes."""

from datetime import datetime
from io import BytesIO, BufferedIOBase
from uuid import UUID
from quart import jsonify, send_file
from service import services, clients, common

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
    clients.cegid.create.opt_return,
    *clients.cegid.create.parameters,
    pos=clients.params.pos,
    **clients.cegid.create.parameterskv,
)
async def create(**kwargs: ...):
    """Crea los datos de los clientes."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    source_payload = "payload.web.files"
    support = kwargs.pop("support", "csv")
    mode = "request"
    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    pos = kwargs.pop("pos", "cegid")
    kwargs.pop("mode", None)
    kwargs.pop("force", None)

    _dataid = dataid(await clients.cegid.create(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        pos=pos,
        force=force,
        **kwargs
    ))

    if _dataid not in clients.data.DS_CLIENTS_POS.persistent:
        clients.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(clients.returns.datajson, fixed=clients.params.fixed)
def get(*, fixed=False):
    """Obtiene los datos de los clientes."""
    [clients_pos, *_] = clients.cegid.get(dataid())
    orientjson = "records" # <- En String JSON - mejor rendimiento
    return clients_pos, fixed, orientjson

@services.operation(clients.cegid.fullfix.opt_return)
def fullfix():
    """Obtiene los datos de los clientes."""
    return clients.cegid.fullfix(dataid())

@services.operation(clients.cegid.pop.opt_return)
def clear():
    """Eliminar el set de datos cargado"""
    return clients.cegid.pop(dataid())

@services.operation(clients.cegid.analyze.opt_return)
def analyze():
    """Obtiene un analisis de los datos de los clientes."""
    return clients.cegid.analyze(dataid())

@services.operation(clients.cegid.exceptions.opt_return)
def exceptions():
    """Obtiene un listado de los errores encontrados en los datos de clientes."""
    return clients.cegid.exceptions(analyze(), dataid=dataid())

@services.operation(
    common.returns.response,
    *clients.cegid.save.parameters,
    filename=common.params.filename,
    **clients.cegid.save.parameterskv
)
async def download(filename: str = None, **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de los clientes."""

    support = kwargs.get("support", "csv")
    destination = kwargs.pop("destination", None) or BytesIO()
    clients.cegid.save(dataid(), destination=destination, **kwargs)

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        now = datetime.now()
        date_str = now.strftime("%Y%m%d_%H%M_%S") + f"{now.microsecond // 1000:03d}"
        filename = f"ClientesHcos_{date_str}"

        if support == "excel":
            filename += ".xlsx"
        else:
            filename += "." + support

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("clients", create, get, clear, fullfix, analyze, exceptions, download)
