"""Modulo para tener un servicio de los datos Clients CEGID: core.clients.pos_cegid"""

from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.clients import (
    ClientsCegid,
    ClientsShopify
)
from service.decorator import services
from service import common, mapfields, data, clients
from utils.typing import JsonFrameOrient

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=clients.params.dataid,
    idmapfields=mapfields.params.dataid,
    force=clients.params.force,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson
)
async def create(source: DataIO = None,
                 /,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 pos: str = "cegid",
                 dataid: UUID = None,
                 idmapfields: UUID = None,
                 force: bool = False,
                 **kwargs: ...):
    """Crea los datos de los clientes CEGID."""
    uuid = await clients.data.create(
        source=source,
        support=support,
        mode=mode,
        pos=pos,
        dataid=dataid,
        idmapfields=idmapfields,
        force=force,
        **kwargs
    )
    return uuid

@services.operation(common.params.index, common.returns.uuids)
def getall(index: slice = None, /, pos="cegid"):
    """Obtener todos los IDs de datos de los clientes CEGID."""
    if index is None:
        index = slice(None, None)

    pos = clients.params.pos(pos)
    if pos == "shopify":
        ClientsPOS = ClientsShopify
    else:
        ClientsPOS = ClientsCegid

    list_ids = [k for k, v in clients.data.DS_CLIENTS_POS.items() if isinstance(v, ClientsPOS)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        clients_pos = clients.data.DS_CLIENTS_POS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de los clientes con el UUID proporcionado."
        raise KeyError(msg) from err
    return clients_pos

@services.operation(
    clients.params.dataid,
    clients.returns.datajson,
    fixed=clients.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: JsonFrameOrient = None):
    """Obtener los datos de los clientes mediante el ID."""
    clients_pos = _datafromid(dataid)
    return clients_pos, fixed, orientjson

@services.operation(clients.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de los clientes"""
    clients_pos = _datafromid(dataid)
    clients_pos.data.drop(clients_pos.data.index, inplace=True, errors="ignore")
    clients_pos.data_pos.drop(clients_pos.data_pos.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos ClientsPOS"

@services.operation(common.params.optional(clients.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de los clientes segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in clients.data.DS_CLIENTS_POS:
        clients.data.DS_CLIENTS_POS.pop(dataid)
    if dataid in clients.data.DS_CLIENTS_POS.persistent:
        clients.data.DS_CLIENTS_POS.persistent.remove(dataid)
    return 0, "se ha quitado los datos ClientsPOS de la cache"

@services.operation(clients.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in clients.data.DS_CLIENTS_POS.persistent:
        clients.data.DS_CLIENTS_POS.persistent.append(dataid)
    else:
        clients.data.DS_CLIENTS_POS.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos ClientsPOS"

@services.operation(clients.params.dataid, common.returns.mapfields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    clients_pos = _datafromid(dataid)
    return list(clients_pos.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=clients.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    clients_pos = _datafromid(dataid)
    clients_pos.sort_fields(fields)
    return 0, "se han organizado los campos de los datos ClientsPOS"

@services.operation(
    clients.params.dataupdate,
    common.returns.exitstatus,
    dataid=clients.params.dataid
)
def fix(dataupdate: dict[tuple[str, str], list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    clients_pos = _datafromid(dataid)
    clients_pos.fix({k: common.params.series(v) for k, v in dataupdate.items()})
    return 0, "se han reparado los datos ClientsPOS"

@services.operation(clients.params.dataid, common.returns.exitstatus)
def normalize(dataid: UUID, /):
    """Normaliza los datos de los clientes."""
    clients_pos = _datafromid(dataid)
    clients_pos.normalize()
    return 0, "se han normalizado los datos ClientsPOS"

@services.operation(clients.params.dataid, clients.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de los clientes."""
    clients_pos = _datafromid(dataid)
    analysis = clients_pos.analyze()
    return analysis

@services.operation(clients.params.analysis, common.returns.exitstatus, dataid=clients.params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de los clientes, mediante un analisis previo."""
    clients_pos = _datafromid(dataid)
    clients_pos.autofix(analysis)
    return 0, "se han auto reparado los datos ClientsPOS"

@services.operation(clients.params.dataid, clients.returns.analysis)
def fullfix(dataid: UUID, /):
    """Autorepara completamente los datos de los clientes."""
    clients_pos = _datafromid(dataid)
    analysis = clients_pos.fullfix()
    return analysis

@services.operation(
    clients.params.analysis,
    clients.returns.exceptions,
    dataid=clients.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de los clientes."""
    clients_pos = _datafromid(dataid)
    list_exception = clients_pos.exceptions(analysis)
    return list_exception

@services.operation(
    clients.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=clients.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=clients.params.excel,
    index=clients.params.index
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         **kwargs: ...):
    """Guarda los datos de los clientes."""
    clients_pos = _datafromid(dataid)
    clients_pos.destination = destination
    clients_pos.save(support, mode, fixed=fixed, **kwargs)
    return 0, "se ha guardado la informacion ClientsPOS"

service = services.service("cegid", create, getall, get, drop, pop, persistent,
                           requiredfields, sortfields, fix, normalize, analyze,
                           autofix, fullfix, exceptions, save)
