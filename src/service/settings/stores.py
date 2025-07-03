"""Modulo para tener un servicio de los datos de las tiendas configuradas."""

from data.io import DataIO, SupportDataIO, ModeDataIO
from core.stores import STORES
from service.decorator import services
from service import common, settings, data
from utils.typing import JsonFrameOrient

@services.operation(settings.returns.datajson, orientjson=common.params.orientjson)
def get(*, orientjson: JsonFrameOrient = None):
    """Obtener los datos de las tiendas."""
    return STORES, True, orientjson

@services.operation(
    common.returns.exitstatus,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=settings.params.excel,
    index=settings.params.index,
    header=common.params.header
)
def save(*,
         destination: DataIO | None = None,
         support: SupportDataIO = "excel",
         mode: ModeDataIO = "raw",
         **kwargs: ...):
    """Guarda los datos de las tiendas."""
    STORES.destination = destination
    STORES.save(support, mode, **kwargs)
    return 0, "se ha guardado la informacion configuracion de tiendas"

service = services.service("stores", get, save)
