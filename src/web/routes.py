"""Modulo para establecer las rutas de la web."""

from flask import render_template
from web.app import app

@app.route("/")
def home():
    """Pagina principal"""
    return render_template("pages/home.html")
