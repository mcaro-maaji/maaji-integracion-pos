"""Modulo para parametrizar la aplicacion Web"""

from pathlib import Path
from quart import Quart

app = Quart(
    import_name="__main__",
    static_folder="..\\static",
    template_folder=Path.cwd() / "..\\templates"
)
