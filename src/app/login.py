"""Modulo para controlar el inicio de session en la aplicacion."""

from os import urandom as os_urandom
from quart import session as quart_session, request, redirect
from utils.env import Environment
from .app import app

app.secret_key = os_urandom(32)

@app.before_request
async def bloquear_app():
    """bloquear las rutas para iniciar session en la app"""

    routes_public = {
        "/login",
        "/static/js",
        "/static/icons",
        "/static/css",
        "/templates",
        "/api/services/app/session",
        "/api/services/app/commands"
    }

    if quart_session.get("authenticate"):
        return
    if Environment.is_login():
        return
    for route_public in routes_public:
        if request.path.startswith(route_public):
            return

    return redirect("/login")
