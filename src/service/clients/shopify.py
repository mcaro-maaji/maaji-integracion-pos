"""Modulo para tener un servicio de los datos ClientsShopifyMx: core.clients.pos_shopify"""

from uuid import UUID
from io import BufferedIOBase
from os import PathLike
from service.decorator import services
import service.clients.cegid as c

@services.operation(c.create.opt_return, *c.create.parameters, **c.create.parameterskv)
async def create(obj: str | bytes | PathLike | BufferedIOBase = None,
                 /,
                 datafrom="raw",
                 dataid: UUID = None,
                 ftype="csv",
                 delimeter="|",
                 encoding="utf-8",
                 idmapfields: UUID = None,
                 force=False):
    """Crea los datos de los clientes Shopify."""
    return await c.create(obj,
                          pos="shopify",
                          datafrom=datafrom,
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

service = services.service("shopify", create, getall, c.get, c.drop, c.pop, c.persistent,
                                   c.requiredfields, c.sortfields, c.fix, c.normalize, c.analyze,
                                   c.autofix, c.fullfix, c.exceptions, c.save)
