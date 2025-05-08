"""Modulo para crear los servicios de la caracteristicas de los clientes."""

__version__ = "1.0.0"

__all__ = [
    "clients_data_service",
    "clients_services",
    "clients_servicesgroup"
]

from service.types import ServicesGroup
from .data import service as clients_data_service

clients_services = [
    clients_data_service
]

clients_servicesgroup = ServicesGroup(name="clients_group", services=clients_services)
