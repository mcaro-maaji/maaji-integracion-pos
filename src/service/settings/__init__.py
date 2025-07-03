"""Modulo para crear los servicios de la caracteristicas de las configuraciones."""

__version__ = "1.0.0"

__all__ = [
    "returns",
    "params",
    "municipios",
    "stores",
    "providers",
    "afi_params"
]

from service.decorator import services
from . import returns, params, municipios, stores, providers, afi_params

group = services.group("settings", municipios.service, stores.service,
                       providers.service, afi_params.service)
