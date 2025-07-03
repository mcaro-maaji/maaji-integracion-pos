"""
Modulo para disponer de todos los recursos a la web a modo de servicio de la interfaz contable.
"""

from datetime import datetime
from io import BytesIO, BufferedIOBase
from uuid import UUID
from quart import jsonify, send_file
from service import services, afi, common

def _generate_dataid(init: UUID = None):
    """Obtener el ID de los datos AFI"""
    _dataid: UUID | None = init

    def get_dataid(value: UUID = None):
        nonlocal _dataid

        if not value is None:
            _dataid = value
        if _dataid is None:
            raise ValueError("no se ha creado un set de datos AFI para leer.")
        return _dataid

    return get_dataid

dataid = _generate_dataid()
transfers_dataid = _generate_dataid()

@services.operation(
    afi.cegid.create.opt_return,
    *afi.cegid.create.parameters,
    **afi.cegid.create.parameterskv,
)
async def create(**kwargs: ...):
    """Crea los datos de la interfaz contable."""
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

    _dataid = dataid(await afi.cegid.create(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in afi.data.DS_AFI.persistent:
        afi.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(
    afi.cegid.create.opt_return,
    *afi.cegid.create.parameters,
    **afi.cegid.create.parameterskv,
)
async def settransfers(**kwargs: ...):
    """Crea los datos de las transferencias zf en interfaz contable."""
    try:
        _dataid = transfers_dataid()
    except ValueError:
        _dataid = None

    source_payload = "payload.web.files"
    support = kwargs.pop("support", "csv")
    mode = "request"
    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    kwargs.pop("mode", None)
    kwargs.pop("force", None)

    _dataid = transfers_dataid(await afi.cegid.settransfers(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    return transfers_dataid()

@services.operation(afi.returns.datajson, fixed=afi.params.fixed)
def get(*, fixed=False):
    """Obtiene los datos de la interfaz contable."""
    [afi_data, *_] = afi.cegid.get(dataid())
    orientjson = "records" # <- En String JSON - mejor rendimiento
    return afi_data, fixed, orientjson

@services.operation(afi.cegid.fullfix.opt_return)
def fullfix():
    """Obtiene los datos de la interfaz contable."""
    try:
        _transfers_dataid = transfers_dataid()
    except ValueError:
        _transfers_dataid = None

    return afi.cegid.fullfix(dataid(), transfers_dataid=_transfers_dataid)

@services.operation(afi.cegid.pop.opt_return)
def clear():
    """Eliminar el set de datos cargado"""
    return afi.cegid.pop(dataid())

@services.operation(afi.cegid.analyze.opt_return)
def analyze():
    """Obtiene un analisis de los datos de la interfaz contable."""
    return afi.cegid.analyze(dataid())

@services.operation(afi.cegid.exceptions.opt_return)
def exceptions():
    """Obtiene un listado de los errores encontrados en los datos de IC."""
    return afi.cegid.exceptions(analyze(), dataid=dataid())

@services.operation(
    common.returns.response,
    *afi.cegid.save.parameters,
    filename=common.params.filename,
    **afi.cegid.save.parameterskv
)
async def download(filename: str = None, **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de la interfaz contable."""

    support = kwargs.get("support", "csv")
    destination = kwargs.pop("destination", None) or BytesIO()
    afi.cegid.save(dataid(), destination=destination, **kwargs)

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        now = datetime.now()
        date_str = now.strftime("%Y%m%d%H%M%S")
        filename = f"IC_{date_str}"

        if support == "excel":
            filename += ".xlsx"
        else:
            filename += "." + support

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("afi", create, settransfers, get, clear, fullfix,
                           analyze, exceptions, download)
