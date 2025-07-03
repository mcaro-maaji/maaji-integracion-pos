"""Modulo para tener un servicio de los datos de los productos CEGID: core.products"""

from datetime import datetime
from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.products import Products
from providers.microsoft.api.dynamics import DynamicsKeyEnv
from service.decorator import services
from service import common, data, products
from utils.typing import JsonFrameOrient

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=products.params.dataid,
    force=products.params.force,
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
    """Crea los datos de los productos CEGID."""
    uuid = await products.data.create(
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
    dynamicsenv=products.params.dynamicsenv,
    dateend=common.params.datetime,
    datestart=common.params.datetime,
    areaid=products.params.areaid,
    dataid=products.params.dataid,
    force=products.params.force
)
async def fromapi(*,
                  dynamicsenv: DynamicsKeyEnv = "PROD",
                  dateend: datetime = None,
                  datestart: datetime = None,
                  areaid: str = None,
                  dataid: UUID = None,
                  force: bool = False,
                  **kwargs: ...):
    """Crea los datos de los productos a partir de la api Dynamics 365."""
    uuid = await products.data.create_fromapi(
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
    """Obtener todos los IDs de datos de los productos CEGID."""
    if index is None:
        index = slice(None, None)

    list_ids = [k for k, v in products.data.DS_PRODUCTS.items() if isinstance(v, Products)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        products_select = products.data.DS_PRODUCTS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de los productos con el UUID proporcionado."
        raise KeyError(msg) from err
    return products_select

@services.operation(
    products.params.dataid,
    products.returns.datajson,
    fixed=products.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: JsonFrameOrient = None):
    """Obtener los datos de los productos mediante el ID."""
    products_select = _datafromid(dataid)
    return products_select, fixed, orientjson

@services.operation(products.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de los productos"""
    products_select = _datafromid(dataid)
    products_select.data.drop(products_select.data.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos Products"

@services.operation(common.params.optional(products.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de los productos segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in products.data.DS_PRODUCTS:
        products.data.DS_PRODUCTS.pop(dataid)
    if dataid in products.data.DS_PRODUCTS.persistent:
        products.data.DS_PRODUCTS.persistent.remove(dataid)
    return 0, "se ha quitado los datos Products de la cache"

@services.operation(products.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in products.data.DS_PRODUCTS.persistent:
        products.data.DS_PRODUCTS.persistent.append(dataid)
    else:
        products.data.DS_PRODUCTS.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos Products"

@services.operation(products.params.dataid, common.returns.fields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    products_select = _datafromid(dataid)
    return list(products_select.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=products.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    products_select = _datafromid(dataid)
    products_select.sort_fields(fields)
    return 0, "se han organizado los campos de los datos Products"

@services.operation(
    products.params.dataupdate,
    common.returns.exitstatus,
    dataid=products.params.dataid
)
def fix(dataupdate: dict[str, list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    products_select = _datafromid(dataid)
    products_select.fix({k: common.params.series(v) for k, v in dataupdate.items()})
    return 0, "se han reparado los datos Products"

@services.operation(products.params.dataid, common.returns.exitstatus)
def normalize(dataid: UUID, /):
    """Normaliza los datos de los productos."""
    products_select = _datafromid(dataid)
    products_select.normalize()
    return 0, "se han normalizado los datos Products"

@services.operation(products.params.dataid, products.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de los productos."""
    # raise NotImplementedError("operacion de servicio no implementada.")
    products_select = _datafromid(dataid)
    analysis = products_select.analyze()
    return analysis

@services.operation(products.params.analysis, common.returns.exitstatus, dataid=products.params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de los productos, mediante un analisis previo."""
    raise NotImplementedError("operacion de servicio no implementada.")
    products_select = _datafromid(dataid)
    products_select.autofix(analysis)
    return 0, "se han auto reparado los datos Products"

@services.operation(products.params.dataid, products.returns.analysis)
def fullfix(dataid: UUID, /):
    """Autorepara completamente los datos de los productos."""
    products_select = _datafromid(dataid)
    analysis = products_select.fullfix()
    return analysis

@services.operation(
    products.params.analysis,
    products.returns.exceptions,
    dataid=products.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de los productos."""
    products_select = _datafromid(dataid)
    list_exception = products_select.exceptions(analysis)
    return list_exception

@services.operation(
    products.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=products.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=products.params.excel,
    index=products.params.index,
    header=common.params.header
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         **kwargs: ...):
    """Guarda los datos de los productos."""
    products_select = _datafromid(dataid)
    products_select.destination = destination
    products_select.save(support, mode, **kwargs)
    return 0, "se ha guardado la informacion Products"

service = services.service("cegid", create, fromapi, getall, get, drop, pop, persistent,
                           requiredfields, sortfields, fix, normalize, analyze,
                           autofix, fullfix, exceptions, save)
