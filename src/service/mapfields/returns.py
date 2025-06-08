"""Modulo para definir devoluciones del servicio de MapFields"""

from service.types import ServiceResult
from service.decorator import services
from utils.mapfields import MapFields

@services.opt_return(type="[[string, string], ...]")
def mapfields(value: MapFields):
    """Devolucion de servicio con el valor de MapFields."""

    if isinstance(value, (tuple, list)):
        return ServiceResult(data=value, type="[[string, string], ...]")
    raise TypeError("el valor debe ser de tipo MapFields.")
