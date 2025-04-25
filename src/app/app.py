"""Modulo para parametrizar la aplicacion Web"""

from pathlib import Path
from flask import Flask

app = Flask(
    import_name="__main__",
    static_folder="..\\static",
    template_folder=Path.cwd() / "..\\templates"
)
