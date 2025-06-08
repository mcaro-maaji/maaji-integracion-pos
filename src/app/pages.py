"""Modulo para establecer las rutas de las paginas web de la aplicacion."""

from quart import Blueprint, render_template
from utils.constants import PATH_TEMPLATES

bp_pages = Blueprint("pages", __name__, url_prefix="/")

PATH_PAGES = PATH_TEMPLATES / "pages"
paths_pages = list(PATH_PAGES.glob("**/*.html"))
paths_pages = [path.as_uri().removeprefix(PATH_PAGES.as_uri()) for path in paths_pages]

for path in paths_pages:
    route = path.removesuffix(".html")
    endpoint = route.replace("/", "-")[1:]
    endpoint = "/pages/" + endpoint.replace(".", "_")

    async def _handler(__path=path):
        return await render_template("pages" + __path)

    bp_pages.add_url_rule(
        route,
        endpoint=endpoint,
        view_func=_handler,
        strict_slashes=False,
    )
