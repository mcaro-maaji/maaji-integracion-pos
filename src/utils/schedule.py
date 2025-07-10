"""Modulo para definir los programadores de tareas, configurar, etc."""

from typing import Literal, TypedDict, TypeGuard
from types import NoneType
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler_app = AsyncIOScheduler(job_defaults={"max_instances": 5})
scheduler_scripts = AsyncIOScheduler(job_defaults={"max_instances": 5})

ScheduleJobStatus = Literal["run", "pause", "removed"]
schedulejob_status: list[ScheduleJobStatus] = ["run", "pause", "removed"]
ScheduleJobTrigger = Literal["interval", "date", "cron"]
schedulejob_trigger: list[ScheduleJobTrigger] = ["interval", "date", "cron"]

def is_schedulejob_status(value) -> TypeGuard[ScheduleJobStatus]:
    """Comprueba que el valor sea de tipo `ScheduleJobStatus`"""
    return value in schedulejob_status

def is_schedulejob_trigger(value) -> TypeGuard[ScheduleJobTrigger]:
    """Comprueba que el valor sea de tipo `ScheduleJobTrigger`"""
    return value in schedulejob_trigger

class ScheduleJobParamsBase(TypedDict):
    """Estructura de parametros para crear un job"""
    id: str | None
    name: str | None
    trigger: Literal["interval"]
    misfire_grace_time: int | None
    coalesce: bool | None
    max_instances: int | None
    next_run_time: str | None
    replace_existing: bool | None

    @classmethod
    def validate(cls, obj) -> TypeGuard["ScheduleJobParamsBase"]:
        """Comprueba de que el objecto sea tipo `ScheduleJobParamsBase`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("id"), (str, NoneType)),
            isinstance(obj.get("name"), (str, NoneType)),
            is_schedulejob_trigger(obj.get("trigger")),
            isinstance(obj.get("misfire_grace_time"), (int, NoneType)),
            isinstance(obj.get("coalesce"), (bool, NoneType)),
            isinstance(obj.get("max_instances"), (int, NoneType)),
            isinstance(obj.get("next_run_time"), (str, NoneType)),
            isinstance(obj.get("replace_existing"), (bool, NoneType))
        ))

class ScheduleJobParamsInterval(TypedDict):
    """Estructura de parametros para crear un job con el trigger interval"""
    id: str
    name: str | None
    trigger: Literal["interval"]
    misfire_grace_time: int | None
    coalesce: bool | None
    max_instances: int | None
    next_run_time: str | None
    replace_existing: bool | None

    weeks: int | None
    days: int | None
    hours: int | None
    minutes: int | None
    seconds: int | None
    start_date: str | datetime | None
    end_date: str | datetime | None
    timezone: str | ZoneInfo | None

    @classmethod
    def validate(cls, obj) -> TypeGuard["ScheduleJobParamsInterval"]:
        """Comprueba de que el objecto sea tipo `ScheduleJobParamsInterval`"""
        if not isinstance(obj, dict):
            return False
        values = (
            (obj.get("weeks"), (int, NoneType)),
            (obj.get("days"), (int, NoneType)),
            (obj.get("hours"), (int, NoneType)),
            (obj.get("minutes"), (int, NoneType)),
            (obj.get("seconds"), (int, NoneType)),
            (obj.get("start_date"), (str, datetime, NoneType)),
            (obj.get("end_date"), (str, datetime, NoneType)),
            (obj.get("timezone"), (str, ZoneInfo, NoneType))
        )
        all_is_none = all(v is None for v, _ in values)
        all_is_type = all(isinstance(v, t) for v, t in values)

        return all((
            ScheduleJobParamsBase.validate(obj),
            obj.get("trigger") == "interval",
            not all_is_none,
            all_is_type
        ))

class ScheduleJobParamsDate(TypedDict):
    """Estructura de parametros para crear un job con el trigger date"""
    id: str
    name: str | None
    trigger: Literal["date"]
    misfire_grace_time: int | None
    coalesce: bool | None
    max_instances: int | None
    next_run_time: str | None
    replace_existing: bool | None

    run_date: str | datetime

    @classmethod
    def validate(cls, obj) -> TypeGuard["ScheduleJobParamsDate"]:
        """Comprueba de que el objecto sea tipo `ScheduleJobParamsDate`"""
        if not isinstance(obj, dict):
            return False
        return all((
            ScheduleJobParamsBase.validate(obj),
            obj.get("trigger") == "date",
            isinstance(obj.get("run_date"), (str, datetime))
        ))

class ScheduleJobParamsCron(TypedDict):
    """Estructura de parametros para crear un job con el trigger cron"""
    id: str
    name: str | None
    trigger: Literal["cron"]
    misfire_grace_time: int | None
    coalesce: bool | None
    max_instances: int | None
    next_run_time: str | None
    replace_existing: bool | None

    year: int | str | None
    month: int | str | None
    day: int | str | None
    week: int | str | None
    day_of_week: int | str | None
    hour: int | str | None
    minute: int | str | None
    second: int | str | None
    start_date: str | datetime | None
    end_date: str | datetime | None
    timezone: str | ZoneInfo | None

    @classmethod
    def validate(cls, obj) -> TypeGuard["ScheduleJobParamsCron"]:
        """Comprueba de que el objecto sea tipo `ScheduleJobParamsCron`"""
        if not isinstance(obj, dict):
            return False
        values = (
            (obj.get("year"), (int, str, NoneType)),
            (obj.get("month"), (int, str, NoneType)),
            (obj.get("day"), (int, str, NoneType)),
            (obj.get("week"), (int, str, NoneType)),
            (obj.get("day_of_week"), (int, str, NoneType)),
            (obj.get("hour"), (int, str, NoneType)),
            (obj.get("minute"), (int, str, NoneType)),
            (obj.get("second"), (int, str, NoneType)),
            (obj.get("start_date"), (str, datetime, NoneType)),
            (obj.get("end_date"), (str, datetime, NoneType)),
            (obj.get("timezone"), (str, ZoneInfo, NoneType))
        )
        all_is_none = all(v is None for v, _ in values)
        all_is_type = all(isinstance(v, t) for v, t in values)

        return all((
            ScheduleJobParamsBase.validate(obj),
            obj.get("trigger") == "cron",
            not all_is_none,
            all_is_type
        ))

ScheduleJobParams = ScheduleJobParamsInterval | ScheduleJobParamsDate | ScheduleJobParamsCron

def is_schedulejob_params(value) -> TypeGuard[ScheduleJobParams]:
    """Comprueba de que sea tipo `ScheduleJobParams`"""
    return (
        ScheduleJobParamsInterval.validate(value) or
        ScheduleJobParamsDate.validate(value) or
        ScheduleJobParamsCron.validate(value)
    )
