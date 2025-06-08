"""Modulo para tener un servicio de los datos ClientsCEGID: core.clients.pos_cegid"""

from uuid import UUID
from io import BytesIO
from quart import request, has_request_context
from utils.typing import FilePath, ReadBuffer
from service import common as c
from service.types import ServiceError
from service.decorator import services
from service.mapfields import params as mf_params
from service.clients import data, params, returns

@services.operation(
    c.params.raw,
    c.returns.uuid,
    ftype=c.params.ftype,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
)
def fromraw(raw: str,
            /,
            pos="cegid",
            ftype="csv",
            delimeter="|",
            encoding="utf-8",
            idmapfields: UUID = None):
    """Crea los datos de los clientes CEGID por medio de un string."""
    raw_bytes = raw.encode(encoding)
    buffer = BytesIO(raw_bytes)
    uuid = data.create(
        buffer,
        pos=pos,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields
    )
    return uuid

@services.operation(
    c.params.fpath,
    c.returns.uuid,
    ftype=c.params.ftype,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
)
def frompath(fpath: FilePath,
             /,
             pos="cegid",
             ftype="csv",
             delimeter="|",
             encoding="utf-8",
             idmapfields: UUID = None):
    """Crea los datos de los clientes CEGID por medio de un ruta (path)."""
    uuid = data.create(
        fpath,
        pos=pos,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields
    )
    return uuid

@services.operation(
    c.returns.uuid,
    ftype=c.params.ftype,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
)
async def fromfile(*,
                   pos="cegid",
                   ftype="csv",
                   delimeter="|",
                   encoding="utf-8",
                   idmapfields: UUID = None):
    """Crea los datos de los clientes CEGID por medio de un archivo."""
    if not has_request_context():
        raise ServiceError("no se ha leido la peticion al servicio correctamente")

    file: ReadBuffer = (await request.files).get("file")
    if not file:
        raise ServiceError("no hay archivo en la peticion del servicio")

    uuid = data.create(
        file,
        pos=pos,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields
    )
    return uuid

@services.operation(c.params.index, c.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes CEGID."""
    if index is None:
        index = slice(None, None)
    return list(data.DS_CLIENTS_POS.keys())[index]

@services.operation(
    params.dataid,
    returns.datajson,
    converted=params.converted,
    orientjson=c.params.orientjson
)
def get(dataid: UUID, /, converted: bool = False, orientjson: c.params.JsonFrameOrient = "records"):
    """Obtener los datos de los clientes CEGID mediante el ID."""
    try:
        clients = data.DS_CLIENTS_POS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de los clientes con el UUID proporcionado."
        raise KeyError(msg) from err

    return clients, converted, orientjson

service_cegid = services.service("cegid", fromraw, frompath, fromfile, getall, get)
