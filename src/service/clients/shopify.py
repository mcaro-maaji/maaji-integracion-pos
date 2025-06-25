"""Modulo para tener un servicio de los datos ClientsShopifyMx: core.pos_shopify"""

from uuid import UUID
from data.io import DataIO, SupportDataIO, ModeDataIO
from service.decorator import services
from service.clients import cegid

@services.operation(
    cegid.create.opt_return,
    *cegid.create.parameters,
    **cegid.create.parameterskv
)
async def create(source: DataIO = None,
                 /,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 dataid: UUID = None,
                 idmapfields: UUID = None,
                 force: bool = False,
                 **kwargs: ...):
    """Crea los datos de los clientes Shopify."""
    return await cegid.create(
        source,
        support=support,
        mode=mode,
        pos="shopify",
        dataid=dataid,
        idmapfields=idmapfields,
        force=force,
        **kwargs
    )

@services.operation(
    cegid.getall.opt_return,
    *cegid.getall.parameters,
    **cegid.getall.parameterskv
)
def getall(index: slice = None):
    """Obtener todos los IDs de datos de los clientes Shopify."""
    return cegid.getall(index, pos="shopify")

service = services.service("shopify", create, getall, cegid.get, cegid.drop, cegid.pop,
                           cegid.persistent, cegid.requiredfields, cegid.sortfields, cegid.fix,
                           cegid.normalize, cegid.analyze, cegid.autofix, cegid.fullfix,
                           cegid.exceptions, cegid.save)
