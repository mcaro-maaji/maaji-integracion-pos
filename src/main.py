"""Modulo de ejecucion principal"""

import asyncio
from app import server as app_server

async def main():
    """Ejecuta el proyecto."""

    parallel_process = [
        app_server
    ]

    await asyncio.gather(*parallel_process)

if __name__ == "__main__":
    asyncio.run(main())
