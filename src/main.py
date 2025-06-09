"""Modulo de ejecucion principal"""

import asyncio
import signal
import lifecycle
import auto
import app

async def main():
    """Ejecuta el proyecto."""
    # Crear las tareas a ejecutar del proyecto.
    task_app = asyncio.create_task(app.server(app.app, app.config_server))
    auto.sheduler.start()

    # Manejar el evento para cancelar la ejecicion del proyecto con una señal.
    signal.signal(signal.SIGINT, lifecycle.handle_shutdown)
    signal.signal(signal.SIGTERM, lifecycle.handle_shutdown)
    # Esperar a la señal para cerrar el proyecto.
    try:
        await lifecycle.stop_event.wait()
    except KeyboardInterrupt:
        print("Log: ejecucion interrumpida por el teclado.")
    finally:
        task_app.cancel()
        auto.sheduler.shutdown()

        parallel_process = [
            task_app
        ]

        await asyncio.gather(*parallel_process, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
