"""Modulo para crear el servidor que ejecuta la aplicacion."""

from hypercorn.asyncio import serve
from hypercorn.config import Config
from .app import app

config = Config()
config.bind = ["127.0.0.1:5585"]

server = serve(app, config)
