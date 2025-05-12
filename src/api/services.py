"""Modulo para registrar los servicios en la API de la aplicacion."""

from flask import Blueprint, jsonify, request
from service import SERVICES_GROUPS
from service.types import ServiceObj, ServiceResult
from .utils import HTTP_ALL_METHODS

bp_services = Blueprint("services", __name__, url_prefix="/services")

routes_services = [path[1:] for path in SERVICES_GROUPS.paths(attr="name")]
routes_services = ["/" + "/".join(route) for route in routes_services]

@bp_services.route("/")
def services_groups():
    """Ruta principal de los servicios."""
    return jsonify(SERVICES_GROUPS.info())

def get_service_obj(__route: str):
    """Busca el servicio mediante la ruta."""
    names_service = tuple(__route.split("/")[1:])
    service_obj = SERVICES_GROUPS[names_service]
    return service_obj

def handle_get_services(service_obj: ServiceObj):
    """Responde con la informacion del servicio."""
    return jsonify(service_obj.info())

def handle_post_services(service_obj: ServiceObj):
    """Ejecuta los servicios y responde con los resultados."""
    service_params = request.get_json()
    result = service_obj.run(service_params)
    return jsonify(result)

def handle_not_method_service(__route: str):
    """Maneja los metodos que no son permitidos en los servicios."""
    name_service = ".".join(__route.split("/")[-2:])
    errs = f"El servicio '{name_service}' no permite el metodo HTTP: '{request.method}'"
    obj = ServiceResult(data=None, type="ServiceNotImplementedError", errs=errs)
    return jsonify(obj), 405

def handler_services(__route: str):
    """Maneja las peticiones de los servicios."""
    service_obj = get_service_obj(__route)

    if request.method == "GET":
        return handle_get_services(service_obj)
    if request.method == "POST":
        return handle_post_services(service_obj)

    return handle_not_method_service(__route)

for route in routes_services:
    endpoint = route.replace("/", "-")[1:]
    endpoint = endpoint.replace(".", "_")

    def _handler(__route=route):
        return handler_services(__route)

    bp_services.add_url_rule(
        route,
        endpoint=endpoint,
        view_func=_handler,
        strict_slashes=False,
        methods=HTTP_ALL_METHODS
    )

@bp_services.route('/<path:invalid_path>', methods=HTTP_ALL_METHODS)
def service_not_found(invalid_path):
    """Respuesta cuando no existe la ruta del servicio."""
    errs = f"No se ha encontrado el servicio: '{invalid_path}'"
    obj = ServiceResult(data=None, type="ServiceNotFound", errs=errs)
    return jsonify(obj), 404
