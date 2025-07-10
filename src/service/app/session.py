"""Modulo de servicios para realizar login en la aplicacion."""

from app.logging import get_logger
from service.decorator import services
from service import common
from utils.env import Environment, exists_key_file
from utils.constants import SALT_KEY

logger = get_logger("app", "services.session.login")

@services.operation(
    common.returns.exitstatus,
    username=common.params.username,
    password=common.params.password
)
def login(*, username: str, password: str):
    """Establece las credenciales de la aplicacion"""
    if not exists_key_file():
        logger.error("no existe el archivo de llave para acceder a la aplicacion.")
        return 2, "no se ha establecido el archivo de llaves"

    Environment.set_salt(SALT_KEY)
    Environment.set_credentials(username.encode(), password.encode())

    if Environment.is_login():
        logger.info("se ha iniciado session correctamente")
        return 0, "se ha iniciado session correctamente"

    logger.info("no se ha logrado iniciar session con las credenciales dadas")
    return 1, "no se ha logrado iniciar session con las credenciales dadas"

service = services.service("session", login)
