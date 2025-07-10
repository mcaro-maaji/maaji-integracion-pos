"""Modulo de ejecucion principal"""

import sys
import asyncio
import signal
import dotenv
import lifecycle
from app import app, server, logging
from utils.env import Environment, IncorrectCredentials
from utils.constants import PATH_STATIC_DATA, SALT_KEY
from utils.schedule import scheduler_app, scheduler_scripts
from auto import scripts

dotenv.load_dotenv(PATH_STATIC_DATA / ".key", override=True)
logger = logging.get_logger("app", "main")

async def auto_clients():
    """Crea las tareas de automatizacion"""
    clients_path = PATH_STATIC_DATA / "auto/clientes.automatizacionpos.json"
    clients_test_path = PATH_STATIC_DATA / "auto/test.clientes.automatizacionpos.json"

    auto_clients = await scripts.services.create(source=clients_test_path, support="json", mode="path")
    scripts.services.execute(auto_clients)

async def auto_afi():
    """Crea las tareas de automatizacion"""
    afi_path = PATH_STATIC_DATA / "auto/interfaz_contable.automatizacionpos.json"
    afi_test_path = PATH_STATIC_DATA / "auto/test.interfaz_contable.automatizacionpos.json"

    auto_afi = await scripts.services.create(source=afi_test_path, support="json", mode="path")
    scripts.services.execute(auto_afi)

async def main():
    """Ejecuta el proyecto."""
    loop = asyncio.get_running_loop()

    # Programar apagado cuando llegue una señal
    if sys.platform != "win32":  # add_signal_handler no funciona en Windows
        loop.add_signal_handler(signal.SIGINT, lifecycle.handle_shutdown)
        loop.add_signal_handler(signal.SIGTERM, lifecycle.handle_shutdown)

    # Crear las tareas a ejecutar del proyecto.
    task_app = asyncio.create_task(server.serve(app.app, server.config))
    task_auto_clients = asyncio.create_task(auto_clients())
    task_auto_afi = asyncio.create_task(auto_afi())
    scheduler_app.start()
    scheduler_scripts.start()

    try:
        await lifecycle.stop_event.wait()
    except KeyboardInterrupt:
        logger.error("Interrupcion de teclado, apagando aplicacion...")
    finally:
        task_app.cancel()
        scheduler_app.shutdown()
        scheduler_scripts.shutdown()

        parallel_process = [
            task_app,
            task_auto_clients,
            task_auto_afi
        ]

        await asyncio.gather(*parallel_process, return_exceptions=True)

if __name__ == "__main__":
    try:
        Environment.login(SALT_KEY)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("saliendo de la aplicacion...")
    except IncorrectCredentials:
        logger.error("las credenciales no son correctas.")
