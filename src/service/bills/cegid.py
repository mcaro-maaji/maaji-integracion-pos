"""Modulo para tener un servicio de los datos de las facturas de compra CEGID: core.bills"""

from datetime import datetime
from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.bills import Bills
from providers.microsoft.api.dynamics import DynamicsKeyEnv
from service.decorator import services
from service import common, data, bills
from utils.typing import JsonFrameOrient

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=bills.params.dataid,
    force=bills.params.force,
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
    """Crea los datos de las facturas CEGID."""
    uuid = await bills.data.create(
        source=source,
        support=support,
        mode=mode,
        dataid=dataid,
        force=force,
        **kwargs
    )
    return uuid

@services.operation(
    common.returns.uuid,
    dynamicsenv=bills.params.dynamicsenv,
    dateend=common.params.datetime,
    datestart=common.params.datetime,
    areaid=bills.params.areaid,
    dataid=bills.params.dataid,
    force=bills.params.force
)
async def fromapi(*,
                  dynamicsenv: DynamicsKeyEnv = "PROD",
                  dateend: datetime = None,
                  datestart: datetime = None,
                  areaid: str = None,
                  dataid: UUID = None,
                  force: bool = False,
                  **kwargs: ...):
    """Crea los datos de las facturas a partir de la api Dynamics 365."""
    uuid = await bills.data.create_fromapi(
        dynamics_env=dynamicsenv,
        date_end=dateend,
        date_start=datestart,
        data_area_id=areaid,
        dataid=dataid,
        force=force,
        **kwargs
    )
    return uuid

@services.operation(common.params.index, common.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de las facturas CEGID."""
    if index is None:
        index = slice(None, None)

    list_ids = [k for k, v in bills.data.DS_BILLS.items() if isinstance(v, Bills)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        bills_select = bills.data.DS_BILLS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de las facturas con el UUID proporcionado."
        raise KeyError(msg) from err
    return bills_select

@services.operation(
    bills.params.dataid,
    bills.returns.datajson,
    fixed=bills.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: JsonFrameOrient = None):
    """Obtener los datos de las facturas mediante el ID."""
    bills_select = _datafromid(dataid)
    return bills_select, fixed, orientjson

@services.operation(bills.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de las facturas"""
    bills_select = _datafromid(dataid)
    bills_select.data.drop(bills_select.data.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos Bills"

@services.operation(common.params.optional(bills.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de las facturas segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in bills.data.DS_BILLS:
        bills.data.DS_BILLS.pop(dataid)
    if dataid in bills.data.DS_BILLS.persistent:
        bills.data.DS_BILLS.persistent.remove(dataid)
    return 0, "se ha quitado los datos Bills de la cache"

@services.operation(bills.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in bills.data.DS_BILLS.persistent:
        bills.data.DS_BILLS.persistent.append(dataid)
    else:
        bills.data.DS_BILLS.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos Bills"

@services.operation(bills.params.dataid, common.returns.fields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    bills_select = _datafromid(dataid)
    return list(bills_select.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=bills.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    bills_select = _datafromid(dataid)
    bills_select.sort_fields(fields)
    return 0, "se han organizado los campos de los datos Bills"

@services.operation(
    bills.params.dataupdate,
    common.returns.exitstatus,
    dataid=bills.params.dataid
)
def fix(dataupdate: dict[str, list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    bills_select = _datafromid(dataid)
    bills_select.fix({k: common.params.series(v) for k, v in dataupdate.items()})
    return 0, "se han reparado los datos Bills"

@services.operation(bills.params.dataid, common.returns.exitstatus)
def normalize(dataid: UUID, /):
    """Normaliza los datos de las facturas."""
    bills_select = _datafromid(dataid)
    bills_select.normalize()
    return 0, "se han normalizado los datos Bills"

@services.operation(bills.params.dataid, bills.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de las facturas."""
    # raise NotImplementedError("operacion de servicio no implementada.")
    bills_select = _datafromid(dataid)
    analysis = bills_select.analyze()
    return analysis

@services.operation(bills.params.analysis, common.returns.exitstatus, dataid=bills.params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de las facturas, mediante un analisis previo."""
    raise NotImplementedError("operacion de servicio no implementada.")
    bills_select = _datafromid(dataid)
    bills_select.autofix(analysis)
    return 0, "se han auto reparado los datos Bills"

@services.operation(bills.params.dataid, bills.returns.analysis)
def fullfix(dataid: UUID, /):
    """Autorepara completamente los datos de las facturas."""
    bills_select = _datafromid(dataid)
    analysis = bills_select.fullfix()
    return analysis

@services.operation(
    bills.params.analysis,
    bills.returns.exceptions,
    dataid=bills.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de las facturas."""
    bills_select = _datafromid(dataid)
    list_exception = bills_select.exceptions(analysis)
    return list_exception

@services.operation(
    bills.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=bills.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=bills.params.excel,
    index=bills.params.index,
    header=common.params.header
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         **kwargs: ...):
    """Guarda los datos de las facturas."""
    bills_select = _datafromid(dataid)
    bills_select.destination = destination
    bills_select.save(support, mode, **kwargs)
    return 0, "se ha guardado la informacion Bills"

service = services.service("cegid", create, fromapi, getall, get, drop, pop, persistent,
                           requiredfields, sortfields, fix, normalize, analyze,
                           autofix, fullfix, exceptions, save)
