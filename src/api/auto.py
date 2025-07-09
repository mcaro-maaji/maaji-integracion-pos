"""Modulo para registrar los servicios en la API de la aplicacion."""

from quart import Blueprint
from auto import SERVICE_GROUP
from .base import register_routes

bp_auto = Blueprint("auto", __name__, url_prefix="/auto")
register_routes(bp_auto, SERVICE_GROUP)
