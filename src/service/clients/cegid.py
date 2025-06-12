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
    dataid=params.dataid,
    ftype=c.params.ftype,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
    force=params.force
)
def fromraw(raw: str,
            /,
            pos="cegid",
            dataid: UUID = None,
            ftype="csv",
            delimeter="|",
            encoding="utf-8",
            idmapfields: UUID = None,
            force=False):
    """Crea los datos de los clientes CEGID por medio de un string."""
    raw_bytes = raw.encode(encoding)
    buffer = BytesIO(raw_bytes)
    uuid = data.create(
        buffer,
        pos=pos,
        dataid=dataid,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields,
        force=force
    )
    return uuid

@services.operation(
    c.params.fpath,
    c.returns.uuid,
    dataid=params.dataid,
    ftype=c.params.ftype,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
    force=params.force
)
def frompath(fpath: FilePath,
             /,
             pos="cegid",
             dataid=params.dataid,
             ftype="csv",
             delimeter="|",
             encoding="utf-8",
             idmapfields: UUID = None,
             force=False):
    """Crea los datos de los clientes CEGID por medio de un ruta (path)."""
    uuid = data.create(
        fpath,
        pos=pos,
        dataid=dataid,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields,
        force=force
    )
    return uuid

@services.operation(
    c.returns.uuid,
    ftype=c.params.ftype,
    dataid=params.dataid,
    delimeter=c.params.delimeter,
    encoding=c.params.encoding,
    idmapfields=mf_params.idmapfields,
    force=params.force
)
async def fromfile(*,
                   pos="cegid",
                   dataid: UUID = None,
                   ftype="csv",
                   delimeter="|",
                   encoding="utf-8",
                   idmapfields: UUID = None,
                   force=False):
    """Crea los datos de los clientes CEGID por medio de un archivo."""
    if not has_request_context():
        raise ServiceError("no se ha leido la peticion al servicio correctamente")

    file: ReadBuffer = (await request.files).get("payload.file")
    if not file:
        raise ServiceError("no hay archivo en la peticion del servicio")

    uuid = data.create(
        file,
        pos=pos,
        dataid=dataid,
        ftype=ftype,
        delimeter=delimeter,
        encoding=encoding,
        idmapfields=idmapfields,
        force=force
    )
    return uuid

@services.operation(c.params.index, c.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes CEGID."""
    if index is None:
        index = slice(None, None)
    return list(data.DS_CLIENTS_POS.keys())[index]

def _datafromid(dataid: UUID, /):
    try:
        clients = data.DS_CLIENTS_POS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de los clientes con el UUID proporcionado."
        raise KeyError(msg) from err
    return clients

@services.operation(
    params.dataid,
    returns.datajson,
    converted=params.converted,
    orientjson=c.params.orientjson
)
def get(dataid: UUID, /, converted: bool = False, orientjson: c.params.JsonFrameOrient = "records"):
    """Obtener los datos de los clientes CEGID mediante el ID."""
    clients = _datafromid(dataid)
    return clients, converted, orientjson

@services.operation(params.dataid, c.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de los clientes"""
    clients = _datafromid(dataid)
    clients.data.drop(clients.data.index, inplace=True, errors="ignore")
    clients.data_pos.drop(clients.data_pos.index, inplace=True, errors="ignore")
    return 0

@services.operation(params.dataid, c.returns.exitstatus)
def pop(dataid: UUID, /):
    """Elimina la data de los clientes segun el ID."""
    drop(dataid)

    if dataid in data.DS_CLIENTS_POS:
        data.DS_CLIENTS_POS.pop(dataid)
    if dataid in data.DS_CLIENTS_POS.persistent:
        data.DS_CLIENTS_POS.persistent.remove(dataid)
    return 0

@services.operation(c.returns.exitstatus)
def poplast():
    """Elimina el ultimo data de los clientes."""
    list_dataid = getall(slice(-1, None))
    if list_dataid:
        pop(list_dataid[0])
    return 0

@services.operation(params.dataid, c.returns.exitstatus)
def togglepersistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in data.DS_CLIENTS_POS.persistent:
        data.DS_CLIENTS_POS.persistent.append(dataid)
    else:
        data.DS_CLIENTS_POS.persistent.remove(dataid)
    return 0

@services.operation(params.dataid, c.returns.mapfields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    clients = _datafromid(dataid)
    return list(clients.no_match_fields())

@services.operation(
    c.params.optional(mf_params.fields),
    c.returns.exitstatus,
    dataid=params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    clients = _datafromid(dataid)
    if not fields is None:
        fields = set(fields)
    # TODO: Revisar, por que usar todos los campos?
    clients.sort_fields(fields)
    return 0

@services.operation(params.dataupdate, c.returns.exitstatus, dataid=params.dataid)
def fix(dataupdate: dict[tuple[str, str], list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    clients = _datafromid(dataid)
    clients.fix({k: c.params.series(v) for k, v in dataupdate.items()})
    return 0

@services.operation(params.dataid, c.returns.exitstatus)
def normalize(dataid: UUID, /):
    """Normaliza los datos de los clientes."""
    clients = _datafromid(dataid)
    clients.normalize()
    return 0

@services.operation(params.dataid, returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de los clientes."""
    clients = _datafromid(dataid)
    analysis = clients.analyze()
    return analysis

@services.operation(params.analysis, c.returns.exitstatus, dataid=params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de los clientes, mediante un analisis previo."""
    clients = _datafromid(dataid)
    clients.autofix(analysis)
    return 0

@services.operation(params.dataid, returns.analysis)
def fullfix(dataid: UUID, /):
    """Autorepara completamente los datos de los clientes."""
    clients = _datafromid(dataid)
    analysis = clients.fullfix()
    return analysis

@services.operation(params.analysis, returns.exceptions, dataid=params.dataid)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de los clientes."""
    clients = _datafromid(dataid)
    list_exception = clients.exceptions(analysis)
    return list_exception

service_cegid = services.service("cegid", fromraw, frompath, fromfile, getall, get, drop,
                                 pop, poplast, togglepersistent, requiredfields, sortfields, fix,
                                 normalize, analyze, autofix, fullfix, exceptions)
