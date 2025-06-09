"""Modulo para controlar el ciclo de vida del proyecto."""

from types import FrameType
from typing import Optional
from signal import Signals
import asyncio

stop_event = asyncio.Event()

def handle_shutdown(_signum: Optional[Signals] = None, _frame: Optional[FrameType] = None):
    """Manjea la señal recibida para cerrar la ejecucion del proyecto."""
    stop_event.set()
