"""Modulo para disponer de todos los recursos a la web a modo de servicio de los precios de venta."""

from datetime import datetime
from io import BytesIO, BufferedIOBase
from uuid import UUID
from quart import jsonify, send_file
from service import services, prices, common

def _generate_dataid(init: UUID = None):
    """Obtener el ID de los datos Prices"""
    _dataid: UUID | None = init

    def get_dataid(value: UUID = None):
        nonlocal _dataid

        if not value is None:
            _dataid = value
        if _dataid is None:
            raise ValueError("no se ha creado un set de datos Prices para leer.")
        return _dataid

    return get_dataid

dataid = _generate_dataid()

@services.operation(
    prices.cegid.create.opt_return,
    *prices.cegid.create.parameters,
    **prices.cegid.create.parameterskv,
)
async def create(**kwargs: ...):
    """Crea los datos de los precios de venta."""
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

    _dataid = dataid(await prices.cegid.create(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in prices.data.DS_PRICES.persistent:
        prices.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(
    prices.cegid.fromapi.opt_return,
    *prices.cegid.fromapi.parameters,
    **prices.cegid.fromapi.parameterskv,
)
async def fromapi(**kwargs: ...):
    """Crea los datos de los precios de venta."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    kwargs.pop("force", None)

    _dataid = dataid(await prices.cegid.fromapi(
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in prices.data.DS_PRICES.persistent:
        prices.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(prices.returns.datajson, fixed=prices.params.fixed)
def get(*, fixed=False):
    """Obtiene los datos de los precios de venta."""
    [prices_data, *_] = prices.cegid.get(dataid())
    orientjson = "records" # <- En String JSON - mejor rendimiento
    return prices_data, fixed, orientjson

@services.operation(
    prices.cegid.fullfix.opt_return,
    *prices.cegid.fullfix.parameters,
    **prices.cegid.fullfix.parameterskv
)
def fullfix(datestart: datetime, dateend: datetime = None):
    """Obtiene los datos de los precios de venta."""
    return prices.cegid.fullfix(dataid(), datestart=datestart, dateend=dateend)

@services.operation(prices.cegid.pop.opt_return)
def clear():
    """Eliminar el set de datos cargado"""
    return prices.cegid.pop(dataid())

@services.operation(prices.cegid.analyze.opt_return)
def analyze():
    """Obtiene un analisis de los datos de los precios de venta."""
    return prices.cegid.analyze(dataid())

@services.operation(prices.cegid.exceptions.opt_return)
def exceptions():
    """Obtiene un listado de los errores encontrados en los datos de los precios de venta."""
    return prices.cegid.exceptions(analyze(), dataid=dataid())

@services.operation(
    common.returns.response,
    *prices.cegid.save.parameters,
    filename=common.params.filename,
    **prices.cegid.save.parameterskv
)
async def download(filename: str = None, **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de los precios de venta."""

    support = kwargs.get("support", "csv")
    destination = kwargs.pop("destination", None) or BytesIO()
    save_data_mod = False
    prices.cegid.save(dataid(), destination=destination, datemod=save_data_mod, **kwargs)

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H-%M-%S")
        filename = f"Tarifas {date_str}"

        if support == "excel":
            filename += ".xlsx"
        else:
            filename += "." + support

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("prices", create, fromapi, get, clear,
                           fullfix, analyze, exceptions, download)
