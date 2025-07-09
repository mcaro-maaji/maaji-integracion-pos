"""Modulo para registrar los servicios en la API de la aplicacion."""

from quart import Blueprint
from scripts import SERVICES_GROUPS
from .base import register_routes

bp_scripts = Blueprint("scripts", __name__, url_prefix="/scripts")
register_routes(bp_scripts, SERVICES_GROUPS)
