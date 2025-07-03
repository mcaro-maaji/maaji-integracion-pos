"""Modulo para crear el servidor que ejecuta la aplicacion."""

from logging import getLogger
from asyncio import CancelledError
from hypercorn.asyncio import serve as _serve
from hypercorn.config import Config
from quart import Quart
from lifecycle import stop_event

logger = getLogger("app")
config = Config()

config.bind = ["127.0.0.1:5585"]
config.loglevel = "critical"

async def shutdown_trigger():
    """Apagar el servidor."""
    await stop_event.wait()
    logger.info("Apagando el servidor...")

async def serve(app: Quart, __config: Config):
    """Ejecuta el servidor de la aplicacion."""
    try:
        logger.info("Corriendo en la URL 'http://%s' (CTRL + C para quitar)", __config.bind[0])
        await _serve(app, __config, shutdown_trigger=shutdown_trigger)
    except CancelledError:
        pass
