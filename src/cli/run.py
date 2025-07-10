"""Modulo para gestionar la aplicacion a travez de la linea de comandos"""

import asyncio
import click
from app.logging import get_logger
from app.main import main
from utils.env import Environment, IncorrectCredentials, exists_key_file
from utils.constants import SALT_KEY

logger = get_logger("app", "cli")

@click.group()
def cli():
    """Un CLI simple."""

@click.command()
@click.option("--auto", is_flag=True)
@click.option("--auto-test", is_flag=True)
def run(auto: bool, auto_test: bool):
    """Corre la aplicacion"""
    if not exists_key_file():
        logger.error("no existe el archivo de llave para acceder a la aplicacion.")

    try:
        if auto:
            Environment.login(SALT_KEY)
        asyncio.run(main(auto, auto_test))
    except KeyboardInterrupt:
        logger.info("saliendo de la aplicacion...")
    except IncorrectCredentials:
        logger.error("las credenciales no son correctas.")
