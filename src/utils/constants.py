"""Modulo para almacenar constantes globales."""

import sys
from time import timezone as _local_timezone
from datetime import timedelta, timezone
from pathlib import Path

def get_root_path() -> Path:
    """Obtiene la ruta cuando se esta en desarrollo y compilado."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent

PATH_ROOT = get_root_path()
PATH_DATA = PATH_ROOT / "data"
PATH_DOCS = PATH_ROOT / "docs"
PATH_STATIC = PATH_ROOT / "static"
PATH_STATIC_DATA = PATH_ROOT / "static/data"
PATH_TEMPLATES = PATH_ROOT / "templates"
SALT_KEY = b"cQNEHnUJwnWJlMYZ7Q7FNJ6G6DHrGsw4S9ayzJV819I="
TZ_LOCAL_OFFSET = timedelta(seconds=_local_timezone * -1)
TZ_LOCAL = timezone(TZ_LOCAL_OFFSET)
