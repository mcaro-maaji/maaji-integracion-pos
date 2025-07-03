"""Modulo para disponer de todos los recursos a la web a modo de servicio de los productos."""

from datetime import datetime
from io import BytesIO, BufferedIOBase
from uuid import UUID
from quart import jsonify, send_file
from service import services, products, common

def _generate_dataid(init: UUID = None):
    """Obtener el ID de los datos Products"""
    _dataid: UUID | None = init

    def get_dataid(value: UUID = None):
        nonlocal _dataid

        if not value is None:
            _dataid = value
        if _dataid is None:
            raise ValueError("no se ha creado un set de datos Products para leer.")
        return _dataid

    return get_dataid

dataid = _generate_dataid()

@services.operation(
    products.cegid.create.opt_return,
    *products.cegid.create.parameters,
    **products.cegid.create.parameterskv,
)
async def create(**kwargs: ...):
    """Crea los datos de los productos."""
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

    _dataid = dataid(await products.cegid.create(
        source_payload,
        support=support,
        mode=mode,
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in products.data.DS_PRODUCTS.persistent:
        products.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(
    products.cegid.fromapi.opt_return,
    *products.cegid.fromapi.parameters,
    **products.cegid.fromapi.parameterskv,
)
async def fromapi(**kwargs: ...):
    """Crea los datos de los productos."""
    try:
        _dataid = dataid()
    except ValueError:
        _dataid = None

    _dataid = kwargs.pop("dataid", _dataid)
    force = True
    kwargs.pop("force", None)

    _dataid = dataid(await products.cegid.fromapi(
        dataid=_dataid,
        force=force,
        **kwargs
    ))

    if _dataid not in products.data.DS_PRODUCTS.persistent:
        products.cegid.persistent(_dataid) # agregar nuevo uuid

    return dataid()

@services.operation(products.returns.datajson, fixed=products.params.fixed)
def get(*, fixed=False):
    """Obtiene los datos de los productos."""
    [products_data, *_] = products.cegid.get(dataid())
    orientjson = "records" # <- En String JSON - mejor rendimiento
    return products_data, fixed, orientjson

@services.operation(products.cegid.fullfix.opt_return)
def fullfix():
    """Obtiene los datos de los productos."""
    return products.cegid.fullfix(dataid())

@services.operation(products.cegid.pop.opt_return)
def clear():
    """Eliminar el set de datos cargado"""
    return products.cegid.pop(dataid())

@services.operation(products.cegid.analyze.opt_return)
def analyze():
    """Obtiene un analisis de los datos de los productos."""
    return products.cegid.analyze(dataid())

@services.operation(products.cegid.exceptions.opt_return)
def exceptions():
    """Obtiene un listado de los errores encontrados en los datos de los productos."""
    return products.cegid.exceptions(analyze(), dataid=dataid())

@services.operation(
    common.returns.response,
    *products.cegid.save.parameters,
    filename=common.params.filename,
    **products.cegid.save.parameterskv
)
async def download(filename: str = None, **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de los productos."""

    support = kwargs.get("support", "csv")
    destination = kwargs.pop("destination", None) or BytesIO()
    products.cegid.save(dataid(), destination=destination, **kwargs)

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H-%M-%S")
        filename = f"Articulos {date_str}"

        if support == "excel":
            filename += ".xlsx"
        else:
            filename += "." + support

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("products", create, fromapi, get, clear,
                           fullfix, analyze, exceptions, download)
