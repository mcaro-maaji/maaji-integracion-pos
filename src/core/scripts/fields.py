"""Modulo para definir los campos de los scripts"""

from typing import TypedDict, TypeGuard
from enum import StrEnum
from utils.schedule import (
    ScheduleJobParams,
    ScheduleJobStatus,
    is_schedulejob_status,
    is_schedulejob_params
)

class ScriptField(StrEnum):
    """Estructura de nombres de los campos de un script."""
    ID = "id"
    NAME = "name"
    DESCRIPTION = "description"
    SCRIPT = "script"
    PARAMETERS = "parameters"
    PARAMETERSKV = "parameterskv"
    CONTEXT = "context"
    SCHEDULE = "schedule"
    SCHEDULE_STATUS = "status"

class ScriptLine(TypedDict):
    """Estructura de una linea de los scripts"""
    id: str
    name: str
    description: str | None
    script: str
    parameters: list[object]
    parameterskv: dict[str, object]
    context: dict[str, object]
    schedule: ScheduleJobParams
    status: ScheduleJobStatus

    @classmethod
    def validate(cls, obj) -> TypeGuard["ScriptLine"]:
        """Comprueba de que el objecto sea tipo `ScriptLine`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("id"), str),
            isinstance(obj.get("name"), str),
            isinstance(obj.get("description"), (str, type(None))),
            isinstance(obj.get("script"), str),
            isinstance(obj.get("parameters"), list),
            isinstance(obj.get("parameterskv"), dict),
            isinstance(obj.get("context"), dict),
            is_schedulejob_params(obj.get("schedule")),
            is_schedulejob_status(obj.get("status"))
        ))
