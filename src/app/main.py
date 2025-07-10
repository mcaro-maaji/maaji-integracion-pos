"""Modulo de ejecucion principal para la aplicacion Web y Automatizacion."""

import sys
import asyncio
import signal
import lifecycle
from app import app, server, logging
from utils.constants import PATH_STATIC_DATA, SALT_KEY
from utils.schedule import scheduler_app, scheduler_scripts
from auto import scripts

logger = logging.get_logger("app", "main")

async def auto_clients(is_test: bool = True):
    """Crea las tareas de automatizacion"""
    clients_path = PATH_STATIC_DATA / "auto/clientes.automatizacionpos.json"
    clients_test_path = PATH_STATIC_DATA / "auto/test.clientes.automatizacionpos.json"
    
    path = clients_test_path if is_test else clients_path

    auto_clients = await scripts.services.create(source=path, support="json", mode="path")
    scripts.services.execute(auto_clients)

async def auto_afi(is_test: bool = True):
    """Crea las tareas de automatizacion"""
    afi_path = PATH_STATIC_DATA / "auto/interfaz_contable.automatizacionpos.json"
    afi_test_path = PATH_STATIC_DATA / "auto/test.interfaz_contable.automatizacionpos.json"

    path = afi_test_path if is_test else afi_path

    auto_afi = await scripts.services.create(source=path, support="json", mode="path")
    scripts.services.execute(auto_afi)

async def main(auto: bool = False, auto_is_test: bool = True):
    """Ejecuta de la aplicacion Web."""
    loop = asyncio.get_running_loop()

    # Programar apagado cuando llegue una señal
    if sys.platform != "win32":  # add_signal_handler no funciona en Windows
        loop.add_signal_handler(signal.SIGINT, lifecycle.handle_shutdown)
        loop.add_signal_handler(signal.SIGTERM, lifecycle.handle_shutdown)

    # Crear las tareas a ejecutar del proyecto.
    task_app = asyncio.create_task(server.serve(app.app, server.config))
    if auto:
        task_auto_clients = asyncio.create_task(auto_clients(auto_is_test))
        task_auto_afi = asyncio.create_task(auto_afi(auto_is_test))
        logger.info("tareas de automatizacion programadas correctamente")
        
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
            task_app
        ]

        if auto:
            parallel_process.append(task_auto_clients)
            parallel_process.append(task_auto_afi)

        await asyncio.gather(*parallel_process, return_exceptions=True)
