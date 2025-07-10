"""Modulo para gestionar la automatizacion de los scripts como servicios."""

from uuid import UUID
from datetime import timedelta
from quart import has_request_context, request
from quart.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError, InternalServerError
from data.store import DataStore
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.scripts import Scripts
from service import services, common, data
from auto import scripts

DS_SCRIPTS: DataStore[Scripts] = DataStore(
    max_length=10,                         # 10 sitios disponibles para crear data scripts.
    max_size=10 * 1e6,                     # 10 Megabytes.
    max_duration=timedelta(minutes=100)    # 10 minutos por script
)

def ds_scripts_calc_size(instance: Scripts):
    """Callback para calcular el tamaño de los datos de los scripts."""
    size = int(instance.data.memory_usage(deep=True).sum())
    return size

DS_SCRIPTS.calc_size = ds_scripts_calc_size

async def source_from_request(source: DataIO, mode: ModeDataIO):
    """Obtiene un fileio desde un contexto de request."""
    if mode == "request":
        if not has_request_context():
            raise InternalServerError("no hay contexto de un request HTTP")

        payload = "payload.files"
        if isinstance(source, str):
            payload = source

        source: FileStorage = (await request.files).get(payload)

        if not source:
            msg = "no se ha encontrado el archivo en la peticion con paylaod/key: " + payload
            raise BadRequestKeyError(msg)

    return source

@services.operation(
    common.params.optional(data.params.source),
    common.returns.uuid,
    support=data.params.support,
    mode=data.params.mode,
    dataid=scripts.params.dataid,
    force=scripts.params.force,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    header=common.params.header,
)
async def create(*,
                 source: DataIO = None,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 dataid: UUID = None,
                 force: bool = False,
                 **kwargs: ...):
    """Crea una instancia de Scripts y la guarda en un DataStore, devuelve el ID."""
    source = await source_from_request(source, mode)
    script_data = Scripts(
        source=source,
        support=support,
        mode=mode,
        **kwargs
    )

    if not isinstance(dataid, UUID) and not dataid is None:
        raise TypeError("el parametro dataid debe ser de tipo string[UUID]")

    uuid = DS_SCRIPTS.append(script_data, force=force)
    if dataid:
        scripts_data = DS_SCRIPTS.pop(uuid)
        DS_SCRIPTS[dataid] = scripts_data
    else:
        dataid = uuid
    return dataid

@services.operation(common.params.index, common.returns.uuids)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los scripts."""
    if index is None:
        index = slice(None, None)

    list_ids = [k for k, v in DS_SCRIPTS.items() if isinstance(v, Scripts)]
    return list_ids[index]

def _datafromid(dataid: UUID, /):
    try:
        scripts_select = DS_SCRIPTS[dataid]
    except KeyError as err:
        msg = "no se ha encontrado los datos de los scripts con el UUID proporcionado."
        raise KeyError(msg) from err
    return scripts_select

@services.operation(
    scripts.params.dataid,
    scripts.returns.datajson,
    fixed=scripts.params.fixed,
    orientjson=common.params.orientjson
)
def get(dataid: UUID, /, fixed: bool = False, orientjson: common.params.JsonFrameOrient = None):
    """Obtener los datos de los scripts mediante el ID."""
    scripts_select = _datafromid(dataid)
    return scripts_select, fixed, orientjson

@services.operation(scripts.params.dataid, common.returns.exitstatus)
def drop(dataid: UUID, /):
    """Elimina toda la informacion de los scripts"""
    scripts_select = _datafromid(dataid)
    scripts_select.data.drop(scripts_select.data.index, inplace=True, errors="ignore")
    return 0, "se han eliminado los datos Scripts"

@services.operation(common.params.optional(scripts.params.dataid), common.returns.exitstatus)
def pop(dataid: UUID = None, /):
    """Elimina la data de los scripts segun el identificador, sin este se elimina el ultimo."""
    if dataid is None:
        list_dataid = getall(slice(-1, None))
        if not list_dataid:
            return 0
        dataid = list_dataid[0]

    drop(dataid)

    if dataid in DS_SCRIPTS:
        DS_SCRIPTS.pop(dataid)
    if dataid in DS_SCRIPTS.persistent:
        DS_SCRIPTS.persistent.remove(dataid)
    return 0, "se ha quitado los datos Scripts de la cache"

@services.operation(scripts.params.dataid, common.returns.exitstatus)
def persistent(dataid: UUID, /):
    """Agregar el ID de los datos a los persistentes."""
    _datafromid(dataid)
    if dataid not in DS_SCRIPTS.persistent:
        DS_SCRIPTS.persistent.append(dataid)
    else:
        DS_SCRIPTS.persistent.remove(dataid)
    return 0, "se han hecho persistente los datos Scripts"

@services.operation(scripts.params.dataid, common.returns.fields)
def requiredfields(dataid: UUID, /):
    """Busca los nombres de los campos que no existen y son requeridos."""
    scripts_select = _datafromid(dataid)
    return list(scripts_select.no_match_fields())

@services.operation(
    common.params.optional(common.params.fields),
    common.returns.exitstatus,
    dataid=scripts.params.dataid
)
def sortfields(fields: list[str] = None, *, dataid: UUID):
    """Ordena los campos segun el nombre."""
    scripts_select = _datafromid(dataid)
    scripts_select.sort_fields(fields)
    return 0, "se han organizado los campos de los datos Scripts"

@services.operation(scripts.params.dataid, scripts.returns.analysis)
def analyze(dataid: UUID, /):
    """Normaliza los datos de los scripts."""
    scripts_select = _datafromid(dataid)
    analysis = scripts_select.analyze()
    return analysis

@services.operation(
    scripts.params.analysis,
    scripts.returns.exceptions,
    dataid=scripts.params.dataid
)
def exceptions(analysis: dict[tuple[str, str], list[int]], *, dataid: UUID):
    """Obtiene todos los errores encontrados de los datos de los scripts."""
    scripts_select = _datafromid(dataid)
    list_exception = scripts_select.exceptions(analysis)
    return list_exception

@services.operation(
    scripts.params.dataid,
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    fixed=scripts.params.fixed,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=scripts.params.excel,
    index=scripts.params.index,
    header=common.params.header
)
def save(dataid: UUID,
         /,
         destination: DataIO | None = None,
         support: SupportDataIO = "csv",
         mode: ModeDataIO = "raw",
         fixed=False,
         **kwargs: ...):
    """Guarda los datos de los scripts."""
    scripts_select = _datafromid(dataid)
    scripts_select.destination = destination
    scripts_select.save(support, mode, **kwargs)
    return 0, "se ha guardado la informacion Scripts"

@services.operation(scripts.params.dataid, common.returns.exitstatus)
def execute(dataid: UUID, /):
    """Correr un script usado el ID."""
    scripts_select = _datafromid(dataid)
    scripts.execute(scripts_select)
    return 0, "se ha establecido un estado los scripts correctamente"

service = services.service("scripts", create, getall, get, drop, pop, persistent, requiredfields,
                           sortfields, analyze, exceptions, save, execute)
