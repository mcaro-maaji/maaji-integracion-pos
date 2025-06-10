"""Modulo para tener un servicio de los datos ClientsShopifyMx: core.clients.pos_shopify"""

from uuid import UUID
from utils.typing import FilePath
from service import common as c
from service.decorator import services
from service.clients import cegid

@services.operation(
    cegid.fromraw.opt_return,
    *cegid.fromraw.parameters,
    **cegid.fromraw.parameterskv
)
def fromraw(raw: str,
            /,
            ftype="csv",
            delimeter=";",
            encoding="utf-8",
            idmapfields: UUID = None,
            force=False):
    """Crea los datos de los clientes Shopify por medio de un string."""
    return cegid.fromraw(raw,
                       pos="shopify",
                       ftype=ftype,
                       delimeter=delimeter,
                       encoding=encoding,
                       idmapfields=idmapfields,
                       force=force)

@services.operation(
    cegid.frompath.opt_return,
    *cegid.frompath.parameters,
    **cegid.frompath.parameterskv
)
def frompath(fpath: FilePath,
             /,
             ftype="csv",
             delimeter=";",
             encoding="utf-8",
             idmapfields: UUID = None,
             force=False):
    """Crea los datos de los clientes Shopify por medio de un ruta (path)."""
    return cegid.frompath(fpath,
                        pos="shopify",
                        ftype=ftype,
                        delimeter=delimeter,
                        encoding=encoding,
                        idmapfields=idmapfields,
                        force=force)

@services.operation(
    cegid.fromfile.opt_return,
    *cegid.fromfile.parameters,
    **cegid.fromfile.parameterskv
)
async def fromfile(*,
                   ftype="csv",
                   delimeter=";",
                   encoding="utf-8",
                   idmapfields: UUID = None,
                   force=False):
    """Crea los datos de los clientes Shopify por medio de un archivo."""
    return await cegid.fromfile(pos="shopify",
                              ftype=ftype,
                              delimeter=delimeter,
                              encoding=encoding,
                              idmapfields=idmapfields,
                              force=force)

@services.operation(
    cegid.getall.opt_return,
    *cegid.getall.parameters,
    **cegid.getall.parameterskv
)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes Shopify."""
    return cegid.getall(index)

@services.operation(
    cegid.get.opt_return,
    *cegid.get.parameters,
    **cegid.get.parameterskv
)
def get(dataid: UUID, /, converted: bool = False, orientjson: c.params.JsonFrameOrient = "records"):
    """Obtener los datos de los clientes Shopify mediante el ID."""
    return cegid.get(dataid, converted=converted, orientjson=orientjson)

service_shopify = services.service("shopify", fromraw, frompath, fromfile, getall, get)
