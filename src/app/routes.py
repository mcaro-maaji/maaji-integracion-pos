"""Modulo para establecer las rutas de la web."""

from quart import render_template
from api import bp_api
from .app import app

app.register_blueprint(bp_api)

@app.route("/")
async def home():
    """Pagina principal"""
    return await render_template("pages/home.html")

@app.route("/clients/cegid")
async def tool_clients_cegid():
    """Pagina para utilizar la herramienta de gestion clientes de CEGID Y2"""
    columns = [{"title": "nombre", "field": "nombre"}]
    data = [{"nombre": "julieta"}, {"nombre": "isabel"}]
    return await render_template("pages/tool_clients_cegid.html", data=data, columns=columns)
