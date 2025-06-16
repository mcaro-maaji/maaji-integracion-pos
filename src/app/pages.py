"""Modulo para establecer las rutas de las paginas web de la aplicacion."""

from quart import Blueprint, redirect, render_template
from utils.constants import PATH_TEMPLATES

bp_pages = Blueprint("pages", __name__, url_prefix="/")

PATH_PAGES = PATH_TEMPLATES / "pages"
paths_pages = list(PATH_PAGES.glob("**/*.html"))
paths_pages = [path.as_uri().removeprefix(PATH_PAGES.as_uri()) for path in paths_pages]

@bp_pages.route("/")
async def pages():
    """Pagina principal"""
    return redirect("/home")

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

@bp_pages.route('/<path:invalid_path>')
async def page_not_found(invalid_path):
    """Respuesta cuando no existe la pagina."""
    return redirect("/not-found")
