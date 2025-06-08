"""Modulo para tener un servicio de los datos ClientsShopifyMx: core.clients.pos_shopify"""

from uuid import UUID
from utils.typing import FilePath
from service import common as c
from service.decorator import services
from service.clients import cegid as pos

@services.operation(
    pos.fromraw.opt_return,
    *pos.fromraw.parameters,
    **pos.fromraw.parameterskv
)
def fromraw(raw: str,
            /,
            ftype="csv",
            delimeter=";",
            encoding="utf-8",
            idmapfields: UUID = None):
    """Crea los datos de los clientes Shopify por medio de un string."""
    return pos.fromraw(raw,
                       pos="shopify",
                       ftype=ftype,
                       delimeter=delimeter,
                       encoding=encoding,
                       idmapfields=idmapfields)

@services.operation(
    pos.frompath.opt_return,
    *pos.frompath.parameters,
    **pos.frompath.parameterskv
)
def frompath(fpath: FilePath,
             /,
             ftype="csv",
             delimeter=";",
             encoding="utf-8",
             idmapfields: UUID = None):
    """Crea los datos de los clientes Shopify por medio de un ruta (path)."""
    return pos.frompath(fpath,
                        pos="shopify",
                        ftype=ftype,
                        delimeter=delimeter,
                        encoding=encoding,
                        idmapfields=idmapfields)

@services.operation(
    pos.fromfile.opt_return,
    *pos.fromfile.parameters,
    **pos.fromfile.parameterskv
)
async def fromfile(*,
                   ftype="csv",
                   delimeter=";",
                   encoding="utf-8",
                   idmapfields: UUID = None):
    """Crea los datos de los clientes Shopify por medio de un archivo."""
    return await pos.fromfile(pos="shopify",
                              ftype=ftype,
                              delimeter=delimeter,
                              encoding=encoding,
                              idmapfields=idmapfields)

@services.operation(
    pos.getall.opt_return,
    *pos.getall.parameters,
    **pos.getall.parameterskv
)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes Shopify."""
    return pos.getall(index)

@services.operation(
    pos.get.opt_return,
    *pos.get.parameters,
    **pos.get.parameterskv
)
def get(dataid: UUID, /, converted: bool = False, orientjson: c.params.JsonFrameOrient = "records"):
    """Obtener los datos de los clientes Shopify mediante el ID."""
    return pos.get(dataid, converted=converted, orientjson=orientjson)

service_shopify = services.service("shopify", fromraw, frompath, fromfile, getall, get)
