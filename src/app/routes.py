"""Modulo para establecer las rutas de la aplicacion."""

from api import bp_api
from .pages import bp_pages
from .app import app

app.register_blueprint(bp_api)
app.register_blueprint(bp_pages)
