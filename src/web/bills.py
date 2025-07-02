"""Modulo para disponer de todos los recursos a la web a modo de servicio de las facturas."""

from datetime import datetime
from io import BytesIO, BufferedIOBase
from uuid import UUID
from quart import jsonify, send_file
from service import services, bills, common

def _generate_dataid(init: UUID = None):
    """Obtener el ID de los datos Bills"""
    _dataid: UUID | None = init

    def get_dataid(value: UUID = None):
        nonlocal _dataid

        if not value is None:
            _dataid = value
        if _dataid is None:
            raise ValueError("no se ha creado un set de datos Bills para leer.")
        return _dataid

    return get_dataid

dataid = _generate_dataid()

@services.operation(
    bills.cegid.create.opt_return,
    *bills.cegid.create.parameters,
    **bills.cegid.create.parameterskv,
)
async def create(**kwargs: ...):
    """Crea los datos de las facturas."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    source_payload = "payload.web.files"
    support = kwargs.pop("support", "csv")
    mode = "request"
    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    kwargs.pop("mode", None)
    kwargs.pop("force", None)

    _dataid = dataid(await bills.cegid.create(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in bills.data.DS_BILLS.persistent:
        bills.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(
    bills.cegid.fromapi.opt_return,
    *bills.cegid.fromapi.parameters,
    **bills.cegid.fromapi.parameterskv,
)
async def fromapi(**kwargs: ...):
    """Crea los datos de las facturas."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    kwargs.pop("force", None)

    _dataid = dataid(await bills.cegid.fromapi(
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in bills.data.DS_BILLS.persistent:
        bills.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(bills.returns.datajson, fixed=bills.params.fixed)
def get(*, fixed=False):
    """Obtiene los datos de las facturas."""
    [bills_data, *_] = bills.cegid.get(dataid())
    orientjson = "records" # <- En String JSON - mejor rendimiento
    return bills_data, fixed, orientjson

@services.operation(bills.cegid.fullfix.opt_return)
def fullfix():
    """Obtiene los datos de las facturas."""
    return bills.cegid.fullfix(dataid())

@services.operation(bills.cegid.pop.opt_return)
def clear():
    """Eliminar el set de datos cargado"""
    return bills.cegid.pop(dataid())

@services.operation(bills.cegid.analyze.opt_return)
def analyze():
    """Obtiene un analisis de los datos de las facturas."""
    return bills.cegid.analyze(dataid())

@services.operation(bills.cegid.exceptions.opt_return)
def exceptions():
    """Obtiene un listado de los errores encontrados en los datos de las facturas."""
    return bills.cegid.exceptions(analyze(), dataid=dataid())

@services.operation(
    common.returns.response,
    *bills.cegid.save.parameters,
    filename=common.params.filename,
    **bills.cegid.save.parameterskv
)
async def download(filename: str = None, **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de las facturas."""

    support = kwargs.get("support", "csv")
    destination = kwargs.pop("destination", None) or BytesIO()
    bills.cegid.save(dataid(), destination=destination, **kwargs)

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H-%M-%S")
        filename = f"Compras {date_str}"

        if support == "excel":
            filename += ".xlsx"
        else:
            filename += "." + support

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("bills", create, fromapi, get, clear,
                           fullfix, analyze, exceptions, download)
