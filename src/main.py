"""Modulo de ejecucion principal"""

from app import logging
from cli.run import run

logger = logging.get_logger("app", "main")

if __name__ == "__main__":
    run()
