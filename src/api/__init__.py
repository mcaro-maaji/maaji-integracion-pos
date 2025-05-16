"""Modulo para crear las APIs de la aplicacion."""

__version__ = "1.0.0"

__all__ = [
    "bp_api",
    "bp_services"
]

from quart import Blueprint
from .services import bp_services

bp_api = Blueprint("api", __name__, url_prefix="/api")

bp_api.register_blueprint(bp_services)
