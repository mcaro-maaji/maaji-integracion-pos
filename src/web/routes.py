"""Modulo para establecer las rutas de la web."""

from flask import render_template
from web.app import app

@app.route("/")
def home():
    """Pagina principal"""
    return render_template("pages/home.html")

@app.route("/tool_clients_cegid")
def tool_clients_cegid():
    """Pagina para utilizar la herramienta de gestion clientes de CEGID Y2"""
    return render_template("pages/tool_clients_cegid.html")
