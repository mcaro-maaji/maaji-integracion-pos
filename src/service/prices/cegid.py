"""Modulo para tener un servicio de los datos de los precios de venta CEGID: core.prices"""

from datetime import datetime
from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.prices import Prices
from core.prices.fields import PriceField
from providers.microsoft.api.dynamics import DynamicsKeyEnv
from service.decorator import services
from service import common, data, prices
from utils.typing import JsonFrameOrient

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=prices.params.dataid,
    force=prices.params.force,
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
    uuid = await prices.data.create(
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
    dynamicsenv=prices.params.dynamicsenv,
    dateend=common.params.datetime,
    datestart=common.params.datetime,
    areaid=prices.params.areaid,
    dataid=prices.params.dataid,
    force=prices.params.force
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
    # Ignorar Fechas, debido a que el servicio Dynamics no esta bien configurado
    datestart = datetime(2024, 1, 1, 0, 0, 0)
    dateend = datetime.now()
    # validar Prices.fullfix para filtrar las fechas correspondientes

    uuid = await prices.data.create_fromapi(
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

    list_ids = [k for k, v in prices.data.DS_PRICES.items() if isinstance(v, Prices)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        prices_select = prices.data.DS_PRICES[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de las facturas con el UUID proporcionado."
        raise KeyError(msg) from err
    return prices_select

@services.operation(
    prices.params.dataid,
    prices.returns.datajson,
    fixed=prices.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: JsonFrameOrient = None):
    """Obtener los datos de las facturas mediante el ID."""
    prices_select = _datafromid(dataid)
    return prices_select, fixed, orientjson

@services.operation(prices.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de las facturas"""
    prices_select = _datafromid(dataid)
    prices_select.data.drop(prices_select.data.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos Prices"

@services.operation(common.params.optional(prices.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de las facturas segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in prices.data.DS_PRICES:
        prices.data.DS_PRICES.pop(dataid)
    if dataid in prices.data.DS_PRICES.persistent:
        prices.data.DS_PRICES.persistent.remove(dataid)
    return 0, "se ha quitado los datos Prices de la cache"

@services.operation(prices.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in prices.data.DS_PRICES.persistent:
        prices.data.DS_PRICES.persistent.append(dataid)
    else:
        prices.data.DS_PRICES.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos Prices"

@services.operation(prices.params.dataid, common.returns.fields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    prices_select = _datafromid(dataid)
    return list(prices_select.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=prices.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    prices_select = _datafromid(dataid)
    prices_select.sort_fields(fields)
    return 0, "se han organizado los campos de los datos Prices"

@services.operation(
    prices.params.dataupdate,
    common.returns.exitstatus,
    dataid=prices.params.dataid
)
def fix(dataupdate: dict[str, list[object]], *, dataid: UUID):
    """Cambia la informacion utilizando los MapFields como columna y los valores como las filas."""
    prices_select = _datafromid(dataid)
    prices_select.fix({k: common.params.series(v) for k, v in dataupdate.items()})
    return 0, "se han reparado los datos Prices"

@services.operation(prices.params.dataid, common.returns.exitstatus)
def normalize(dataid: UUID, /):
    """Normaliza los datos de las facturas."""
    prices_select = _datafromid(dataid)
    prices_select.normalize()
    return 0, "se han normalizado los datos Prices"

@services.operation(prices.params.dataid, prices.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de las facturas."""
    # raise NotImplementedError("operacion de servicio no implementada.")
    prices_select = _datafromid(dataid)
    analysis = prices_select.analyze()
    return analysis

@services.operation(prices.params.analysis, common.returns.exitstatus, dataid=prices.params.dataid)
def autofix(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Autorepara los datos de las facturas, mediante un analisis previo."""
    raise NotImplementedError("operacion de servicio no implementada.")
    prices_select = _datafromid(dataid)
    prices_select.autofix(analysis)
    return 0, "se han auto reparado los datos Prices"

@services.operation(
    prices.params.dataid,
    prices.returns.analysis,
    datestart=common.params.datetime,
    dateend=common.params.datetime,
)
def fullfix(dataid: UUID, /, datestart: datetime, dateend: datetime = None):
    """Autorepara completamente los datos de las facturas."""
    prices_select = _datafromid(dataid)
    analysis = prices_select.fullfix(datestart, dateend)
    return analysis

@services.operation(
    prices.params.analysis,
    prices.returns.exceptions,
    dataid=prices.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de las facturas."""
    prices_select = _datafromid(dataid)
    list_exception = prices_select.exceptions(analysis)
    return list_exception

@services.operation(
    prices.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=prices.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=prices.params.excel,
    index=prices.params.index,
    header=common.params.header,
    datemod=common.params.boolean
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         datemod=False,
         **kwargs: ...):
    """Guarda los datos de las facturas."""
    prices_select = _datafromid(dataid)
    prices_select.destination = destination

    # Guardar los datos sin la fecha de modificacion
    if not datemod:
        fields = [
            PriceField.ID_INTEGRACION,
            PriceField.MONEDA,
            PriceField.CODIGO,
            PriceField.EAN,
            PriceField.PRECIO
        ]
        data_original = prices_select.data.copy()
        prices_select.data = prices_select.data[fields]
    else:
        data_original = prices_select.data

    prices_select.save(support, mode, **kwargs)
    prices_select.data = data_original
    return 0, "se ha guardado la informacion Prices"

service = services.service("cegid", create, fromapi, getall, get, drop, pop, persistent,
                           requiredfields, sortfields, fix, normalize, analyze,
                           autofix, fullfix, exceptions, save)
