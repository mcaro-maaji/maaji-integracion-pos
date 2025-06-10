"""Modulo para definir parametros del servicio de clients: core.clients"""

from uuid import UUID
from service.decorator import services
from service.common import params

@services.parameter(type="'cegid' | 'shopify'")
def pos(value: str):
    """Parametro para elegir el POS que se usara en la operacion."""
    value = str(value).lower()

    if value in ["cegid", "shopify"]:
        return value
    raise ValueError("se debe elegir el alguno de estos valores: 'cegid' | 'shopify'")

@services.parameter(type="ClientsPOS[UUID]")
def dataid(value: str | UUID):
    """Parametro para contiene el ID de los campos de los clientes."""
    return params.uuid(value)

@services.parameter(type="boolean")
def converted(value: bool = False):
    """Parametro para escoger si data de clientes son los convertidos o no por MapFields."""
    return params.boolean(value)

@services.parameter(type="boolean")
def force(value: bool = False):
    """Parametro para forzar la creacion de los datos de los clientes, hace espacio en memoria."""
    return params.boolean(value)
