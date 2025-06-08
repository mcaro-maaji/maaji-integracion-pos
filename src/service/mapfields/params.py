"""Modulo para definir parametros del servicio de MapFields: utils.mapfields"""

from uuid import UUID
from service.decorator import services
from service.common import params

@services.parameter(type="MapFields[UUID]")
def idmapfields(value: str | UUID):
    """Parametro para contiene el ID del mapeo de campos de los clientes."""
    return params.uuid(value)
