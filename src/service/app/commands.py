"""Modulo de servicios para realizar shutdown en la aplicacion."""

from quart import jsonify
from service.decorator import services
from service import common
from lifecycle import handle_shutdown

@services.operation(common.returns.exitstatus)
def shutdown():
    """Apaga la aplicacion"""
    handle_shutdown()
    return 0, "se ha apagado la aplicacion correctamente"

service = services.service("commands", shutdown)
