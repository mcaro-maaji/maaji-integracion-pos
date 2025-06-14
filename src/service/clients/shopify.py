"""Modulo para tener un servicio de los datos ClientsShopifyMx: core.clients.pos_shopify"""

from uuid import UUID
from utils.typing import FilePath
from service.decorator import services
import service.clients.cegid as c

@services.operation(c.fromraw.opt_return, *c.fromraw.parameters, **c.fromraw.parameterskv)
def fromraw(raw: str,
            /,
            dataid: UUID = None,
            ftype="csv",
            delimeter=";",
            encoding="utf-8",
            idmapfields: UUID = None,
            force=False):
    """Crea los datos de los clientes Shopify por medio de un string."""
    return c.fromraw(raw,
                       pos="shopify",
                       dataid=dataid,
                       ftype=ftype,
                       delimeter=delimeter,
                       encoding=encoding,
                       idmapfields=idmapfields,
                       force=force)

@services.operation(c.frompath.opt_return, *c.frompath.parameters, **c.frompath.parameterskv)
def frompath(fpath: FilePath,
             /,
             dataid: UUID = None,
             ftype="csv",
             delimeter=";",
             encoding="utf-8",
             idmapfields: UUID = None,
             force=False):
    """Crea los datos de los clientes Shopify por medio de un ruta (path)."""
    return c.frompath(fpath,
                        pos="shopify",
                        dataid=dataid,
                        ftype=ftype,
                        delimeter=delimeter,
                        encoding=encoding,
                        idmapfields=idmapfields,
                        force=force)

@services.operation(c.fromfile.opt_return, *c.fromfile.parameters, **c.fromfile.parameterskv)
async def fromfile(*,
                   dataid: UUID = None,
                   ftype="csv",
                   delimeter=";",
                   encoding="utf-8",
                   idmapfields: UUID = None,
                   force=False):
    """Crea los datos de los clientes Shopify por medio de un archivo."""
    return await c.fromfile(pos="shopify",
                                dataid=dataid,
                                ftype=ftype,
                                delimeter=delimeter,
                                encoding=encoding,
                                idmapfields=idmapfields,
                                force=force)

@services.operation(c.getall.opt_return, *c.getall.parameters, **c.getall.parameterskv)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes Shopify."""
    return c.getall(index, pos="shopify")

service_shopify = services.service("shopify", fromraw, frompath, fromfile, getall, c.get,
                                   c.drop, c.pop, c.persistent, c.requiredfields,
                                   c.sortfields, c.fix, c.normalize, c.analyze,
                                   c.autofix, c.fullfix, c.exceptions)
