"""Modulo para parametrizar la aplicacion Web"""

from quart import Quart
from utils.constants import PATH_STATIC, PATH_TEMPLATES

app = Quart(
    import_name="__main__",
    static_folder=str(PATH_STATIC),
    template_folder=str(PATH_TEMPLATES)
)
