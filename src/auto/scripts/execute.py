"""Modulo para establecer un estado de ejecucion de los scripts"""

from typing import Callable
from apscheduler.job import Job
from app.logging import get_logger
from service.types import ServiceOperation, ServiceNotFound, ServiceError
from core.scripts import Scripts
from core.scripts.fields import ScriptLine
from scripts import SERVICES_GROUPS as SERVICES
from utils.schedule import scheduler_scripts

logger = get_logger("auto", "scripts")

class ScriptErrorExecution(Exception):
    """Error en la ejecucion de un script."""

def validate(scripts: Scripts):
    """Comprueba que todas las lineas de los scripts."""
    list_scripts = scripts.data.copy().to_dict(orient="records")
    script_lines: list[ScriptLine] = []

    for line in list_scripts:
        if not ScriptLine.validate(line):
            raise TypeError("el script contiene una linea que no es tipo ScriptLine")
        script_lines.append(line)

    return script_lines

def lookup_service(script_line: ScriptLine):
    """Busca en los servicios de los scripts el nombre de uno y lo devuelve."""
    service_name = script_line["script"]
    service_path = service_name.split(".")
    service_obj = SERVICES.get(*service_path)

    if service_obj is None:
        msg = f"no se encuentra el servicio con el nombre: '{service_name}'"
        raise ServiceNotFound(msg)

    if not isinstance(service_obj, ServiceOperation):
        msg = f"no se define como una operacion de servicio: '{service_name}'"
        raise ServiceError(msg)

    return service_obj

def runner_script(script_line: ScriptLine, context: dict[str, object]):
    """Devuelve un callback con que prepara la ejecucion de un `ScriptLine`."""
    service = lookup_service(script_line)
    context.update(script_line["context"])

    async def run_script():
        name = script_line["name"]
        parameters = script_line["parameters"]
        parameterskv = script_line["parameterskv"]
        try:
            logger.info("corriendo la tarea con nombre '%s'", name)
            await service.run(*parameters, **parameterskv, context=context)
            logger.info("la tarea con nombre '%s' finalizo con exito", name)
        except ServiceError as err:
            msg = "en la ejecucion de la tarea con nombre '%s' ocurrio un error: %s"
            logger.error(msg, name, str(err))

    return run_script

def schedule_script(script_line: ScriptLine, runner: Callable):
    """Controla las tareas programadas de los scripts."""
    id_script = script_line["id"] or "script_default"
    job_params = script_line["schedule"].copy()
    id_job = job_params.pop("id", None) or "schedule_default"
    id_default_job = "script_default.schedule_default"
    real_id_job = id_script + "." + id_job

    trigger = job_params.pop("trigger")
    replace = job_params.pop("replace_existing", True)
    job_status = script_line["status"]
    job: Job = scheduler_scripts.get_job(real_id_job)

    if real_id_job == id_default_job:
        replace = True

    if job is None:
        job = scheduler_scripts.add_job(
            runner,
            trigger,
            **job_params,
            id=real_id_job,
            replace_existing=replace
        )

    if job_status == "run":
        job.resume()
    elif job_status == "pause":
        job.pause()
    else:
        job.remove()

def execute(scripts: Scripts):
    """Lee los datos de los scripts y ejecuta los comandos correspondientes."""
    script_lines = validate(scripts)
    context = {}

    for line in script_lines:
        runner = runner_script(line, context)
        schedule_script(line, runner)
