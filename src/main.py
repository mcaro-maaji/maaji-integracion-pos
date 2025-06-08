"""Modulo de ejecucion principal"""

import asyncio
import app

async def main():
    """Ejecuta el proyecto."""

    parallel_process = [
        app.server(app.app, app.config_server)
    ]

    await asyncio.gather(*parallel_process)

if __name__ == "__main__":
    asyncio.run(main())
