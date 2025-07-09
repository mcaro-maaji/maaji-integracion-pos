"""Modulo para crear las APIs de la aplicacion."""

__version__ = "1.0.0"

__all__ = [
    "bp_api",
    "bp_services",
    "bp_web"
]

from quart import Blueprint
from .services import bp_services
from .web import bp_web
from .scripts import bp_scripts
from .auto import bp_auto

bp_api = Blueprint("api", __name__, url_prefix="/api")

# TODO: condicion para registrar desde la configuracion de la aplicacion al inicializar.
bp_api.register_blueprint(bp_services)
bp_api.register_blueprint(bp_web)
bp_api.register_blueprint(bp_scripts)
bp_api.register_blueprint(bp_auto)
