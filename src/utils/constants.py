"""Modulo para almacenar constantes globales."""

from pathlib import Path

PATH_ROOT = Path(__file__).resolve()
PATH_ROOT = PATH_ROOT.parent.parent.parent
PATH_DATA = PATH_ROOT / "data"
PATH_DOCS = PATH_ROOT / "docs"
PATH_STATIC = PATH_ROOT / "static"
PATH_TEMPLATES = PATH_ROOT / "templates"
SALT_KEY = b"VXOSphnDMkK_sU6Bg0dK7lwdF3yoCr-wVz9CbYFVIjw="