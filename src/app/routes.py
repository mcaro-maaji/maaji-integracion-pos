"""Modulo para establecer las rutas de la web."""

from flask import render_template
from .app import app

@app.route("/")
def home():
    """Pagina principal"""
    return render_template("pages/home.html")

@app.route("/tool/clients/cegid")
def tool_clients_cegid():
    """Pagina para utilizar la herramienta de gestion clientes de CEGID Y2"""
    columns = [{"title": "nombre", "field": "nombre"}]
    data = [{"nombre": "julieta"}, {"nombre": "isabel"}]
    return render_template("pages/tool_clients_cegid.html", data=data, columns=columns)
