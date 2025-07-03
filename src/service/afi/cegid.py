"""Modulo para tener un servicio de los datos de la interfaz contable de compra CEGID: core.afi"""

from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.afi import AFI
from service.decorator import services
from service import common, data, afi
from utils.typing import JsonFrameOrient

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=afi.params.dataid,
    force=afi.params.force,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    header=common.params.header,
)
async def create(source: DataIO = None,
                 /,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 dataid: UUID = None,
                 force: bool = False,
                 **kwargs: ...):
    """Crea los datos de la interfaz contable CEGID."""
    uuid = await afi.data.create(
        source=source,
        support=support,
        mode=mode,
        dataid=dataid,
        force=force,
        **kwargs
    )
    return uuid

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=afi.params.dataid,
    force=afi.params.force,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    header=common.params.header,
)
async def settransfers(source: DataIO = None,
                       /,
                       support: SupportDataIO = "csv",
                       mode: ModeDataIO = "raw",
                       dataid: UUID = None,
                       force: bool = False,
                       **kwargs: ...):
    """Crea los datos de las transferencias zf de interfaz contable CEGID."""
    uuid = await afi.data.create_transfers(
        source=source,
        support=support,
        mode=mode,
        dataid=dataid,
        force=force,
        **kwargs
    )
    return uuid

@services.operation(common.params.index, common.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de la interfaz contable CEGID."""
    if index is None:
        index = slice(None, None)

    list_ids = [k for k, v in afi.data.DS_AFI.items() if isinstance(v, AFI)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        afi_select = afi.data.DS_AFI[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de la interfaz contable con el UUID proporcionado."
        raise KeyError(msg) from err
    return afi_select

def _datafromid_transfers(dataid: UUID, /):
    try:
        afi_transfers_select = afi.data.DS_AFI_TRANFERS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de la interfaz contable con el UUID proporcionado."
        raise KeyError(msg) from err
    return afi_transfers_select

@services.operation(
    afi.params.dataid,
    afi.returns.datajson,
    fixed=afi.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: JsonFrameOrient = None):
    """Obtener los datos de la interfaz contable mediante el ID."""
    afi_select = _datafromid(dataid)
    return afi_select, fixed, orientjson

@services.operation(afi.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de la interfaz contable"""
    afi_select = _datafromid(dataid)
    afi_select.data.drop(afi_select.data.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos AFI"

@services.operation(common.params.optional(afi.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de la interfaz contable segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in afi.data.DS_AFI:
        afi.data.DS_AFI.pop(dataid)
    if dataid in afi.data.DS_AFI.persistent:
        afi.data.DS_AFI.persistent.remove(dataid)
    return 0, "se ha quitado los datos AFI de la cache"

@services.operation(afi.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in afi.data.DS_AFI.persistent:
        afi.data.DS_AFI.persistent.append(dataid)
    else:
        afi.data.DS_AFI.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos AFI"

@services.operation(afi.params.dataid, common.returns.fields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    afi_select = _datafromid(dataid)
    return list(afi_select.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=afi.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    afi_select = _datafromid(dataid)
    afi_select.sort_fields(fields)
    return 0, "se han organizado los campos de los datos AFI"

@services.operation(
    afi.params.dataupdate,
    common.returns.exitstatus,
    dataid=afi.params.dataid
)
def fix(dataupdate: dict[str, list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    afi_select = _datafromid(dataid)
    afi_select.fix({k: common.params.series(v) for k, v in dataupdate.items()})
    return 0, "se han reparado los datos AFI"

@services.operation(
    afi.params.dataid,
    afi.returns.analysis,
    transfers_dataid=afi.params.dataid
)
def normalize(dataid: UUID, *, transfers_dataid: UUID = None):
    """Normaliza los datos de la interfaz contable."""
    afi_select = _datafromid(dataid)
    if not transfers_dataid is None:
        afi_transfers = _datafromid_transfers(transfers_dataid)
    else:
        afi_transfers = None
    afi_select.normalize(afi_transfers)
    return 0, "se han normalizado los datos AFI"

@services.operation(afi.params.dataid, afi.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de la interfaz contable."""
    # raise NotImplementedError("operacion de servicio no implementada.")
    afi_select = _datafromid(dataid)
    analysis = afi_select.analyze()
    return analysis

@services.operation(afi.params.analysis, common.returns.exitstatus, dataid=afi.params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de la interfaz contable, mediante un analisis previo."""
    raise NotImplementedError("operacion de servicio no implementada.")
    afi_select = _datafromid(dataid)
    afi_select.autofix(analysis)
    return 0, "se han auto reparado los datos AFI"

@services.operation(
    afi.params.dataid,
    afi.returns.analysis,
    transfers_dataid=afi.params.dataid
)
def fullfix(dataid: UUID, *, transfers_dataid: UUID = None):
    """Autorepara completamente los datos de la interfaz contable."""
    afi_select = _datafromid(dataid)
    if not transfers_dataid is None:
        afi_transfers = _datafromid_transfers(transfers_dataid)
    else:
        afi_transfers = None
    analysis = afi_select.fullfix(afi_transfers)
    return analysis

@services.operation(
    afi.params.analysis,
    afi.returns.exceptions,
    dataid=afi.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de la interfaz contable."""
    afi_select = _datafromid(dataid)
    list_exception = afi_select.exceptions(analysis)
    return list_exception

@services.operation(
    afi.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=afi.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=afi.params.excel,
    index=afi.params.index,
    header=common.params.header
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         **kwargs: ...):
    """Guarda los datos de la interfaz contable."""
    afi_select = _datafromid(dataid)
    afi_select.destination = destination
    afi_select.save(support, mode, **kwargs)
    return 0, "se ha guardado la informacion AFI"

service = services.service("cegid", create, settransfers, getall, get, drop, pop, persistent,
                           requiredfields, sortfields, fix, normalize, analyze,
                           autofix, fullfix, exceptions, save)
