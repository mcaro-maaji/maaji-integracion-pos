"""Modulo para registrar los servicios en la API de la aplicacion."""

from quart import Blueprint
from web import SERVICES_GROUP
from .base import register_routes

bp_web = Blueprint("web", __name__, url_prefix="/web")
register_routes(bp_web, SERVICES_GROUP)
