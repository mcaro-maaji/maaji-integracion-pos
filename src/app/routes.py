"""Modulo para establecer las rutas de la aplicacion."""

from quart import redirect
from api import bp_api
from .pages import bp_pages
from .app import app

app.register_blueprint(bp_pages)
app.register_blueprint(bp_api)

@app.route("/")
async def pages():
    """Pagina principal"""
    return redirect("home")
