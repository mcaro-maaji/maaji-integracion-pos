"""Modulo para registrar los servicios en la API de la aplicacion."""

import json
from quart import Blueprint, jsonify, request
from service import SERVICES_GROUPS, ServiceObj
from service.types import ServiceResult, is_service_params, ServiceParamError
from .utils import HTTP_ALL_METHODS

bp_services = Blueprint("services", __name__, url_prefix="/services")

routes_services = [path[1:] for path in SERVICES_GROUPS.paths(attr="name")]
routes_services = ["/" + "/".join(route) for route in routes_services]

@bp_services.route("/")
async def services_groups():
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

async def get_service_params():
    """Obtiene los parametros de los servicios dependiendo del tipo de peticion."""
    content_type = request.content_type or "application/json"
    msgerr = "error al decodificar el json de los parametros del servicio"

    if content_type.startswith("application/json"):
        service_params = await request.get_json(force=True, silent=True)
        if service_params is None:
            raise ServiceParamError(msgerr)
        if not service_params:
            service_params = {"parameters": []}
    elif content_type.startswith("multipart/form-data"):
        form = await request.form
        payload_parameters = form.get("payload.parameters") or "[]"
        payload_parameterskv = form.get("payload.parameterskv") or "{}"
        payload = "{" + f"""
            "parameters": {payload_parameters},
            "parameterskv": {payload_parameterskv}
        """ + "}"

        try:
            service_params = json.loads(payload)
        except json.JSONDecodeError as err:
            raise ServiceParamError(msgerr + ": " + str(err)) from err
    else:
        raise ServiceParamError("no se han cargado parametros del servicio en la peticion.")

    if not is_service_params(service_params):
        raise ServiceParamError("los parametros de servicio no son correctos.")

    return service_params

async def handle_post_services(service_obj: ServiceObj):
    """Ejecuta los servicios y responde con los resultados."""
    try:
        params = await get_service_params()
    except ServiceParamError as err:
        result = ServiceResult(data=None, type="ServiceParamError", errs=str(err))
    else:
        parameters = params.get("parameters", [])
        parameterskv = params.get("parameterskv", {})
        result = await service_obj.run(*parameters, **parameterskv)

    return result

def handle_not_method_service(__route: str):
    """Maneja los metodos que no son permitidos en los servicios."""
    name_service = ".".join(__route.split("/")[-2:])
    errs = f"el servicio '{name_service}' no permite el metodo HTTP: '{request.method}'"
    obj = ServiceResult(data=None, type="ServiceNotImplementedError", errs=errs)

    return jsonify(obj), 405

async def handler_services(__route: str):
    """Maneja las peticiones de los servicios."""
    service_obj = get_service_obj(__route)

    if request.method == "GET":
        return handle_get_services(service_obj)
    if request.method == "POST":
        return await handle_post_services(service_obj)

    return handle_not_method_service(__route)

for route in routes_services:
    endpoint = route.replace("/", "-")[1:]
    endpoint = endpoint.replace(".", "_")

    async def _handler(__route=route):
        return await handler_services(__route)

    bp_services.add_url_rule(
        route,
        endpoint=endpoint,
        view_func=_handler,
        strict_slashes=False,
        methods=HTTP_ALL_METHODS
    )

@bp_services.route('/<path:invalid_path>', methods=HTTP_ALL_METHODS)
async def service_not_found(invalid_path):
    """Respuesta cuando no existe la ruta del servicio."""
    errs = f"no se ha encontrado el servicio: '{invalid_path}'"
    obj = ServiceResult(data=None, type="ServiceNotFound", errs=errs)

    return jsonify(obj), 404
