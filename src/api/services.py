"""Modulo para registrar los servicios en la API de la aplicacion."""

from quart import Blueprint
from service import SERVICES_GROUPS
from .base import register_routes

bp_services = Blueprint("services", __name__, url_prefix="/services")
register_routes(bp_services, SERVICES_GROUPS)
