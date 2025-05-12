"""Modulo para establecer las rutas de la web."""

from flask import render_template, jsonify
from api import bp_api
from .app import app

app.register_blueprint(bp_api)

@app.route("/")
def home():
    """Pagina principal"""
    # return render_template("pages/home.html")
    return jsonify([i.endpoint for i in app.url_map.iter_rules()])

@app.route("/tool/clients/cegid")
def tool_clients_cegid():
    """Pagina para utilizar la herramienta de gestion clientes de CEGID Y2"""
    columns = [{"title": "nombre", "field": "nombre"}]
    data = [{"nombre": "julieta"}, {"nombre": "isabel"}]
    return render_template("pages/tool_clients_cegid.html", data=data, columns=columns)
