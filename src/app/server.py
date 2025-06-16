"""Modulo para crear el servidor que ejecuta la aplicacion."""

from asyncio import CancelledError
from hypercorn.asyncio import serve as _serve
from hypercorn.config import Config
from quart import Quart
from lifecycle import stop_event

config = Config()
config.bind = ["127.0.0.1:5585"]

async def shutdown_trigger():
    """Apagar el servidor."""
    await stop_event.wait()

async def serve(app: Quart, __config: Config):
    """Ejecuta el servidor de la aplicacion."""
    try:
        await _serve(app, __config, shutdown_trigger=shutdown_trigger)
    except CancelledError:
        print("Log: App Server cancelado.")
