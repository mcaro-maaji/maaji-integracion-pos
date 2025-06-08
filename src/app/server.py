"""Modulo para crear el servidor que ejecuta la aplicacion."""

from hypercorn.asyncio import serve
from hypercorn.config import Config

config_server = Config()
config_server.bind = ["127.0.0.1:5585"]
server = serve
