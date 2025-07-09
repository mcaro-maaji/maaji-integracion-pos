"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de scripts."""

from typing import Literal
from enum import StrEnum
from .fields import ScriptField

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = ScriptField | IDMSG

MSG_EXCEP_SCRIPTS: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    ScriptField.ID: "el id de los scriptlines deben ser unicos",
    ScriptField.NAME: "se debe asiganar un nombre al script.",
    ScriptField.SCRIPT: "no se ha identificado los scripts",
    ScriptField.PARAMETERS: "los parametros debe ser de tipo JSONLike[Array]",
    ScriptField.PARAMETERSKV: "los parametros clave valor debe ser de tipo JSON",
    ScriptField.CONTEXT: "el contexto debe ser tipo JSON",
    ScriptField.SCHEDULE: "los parametros clave valor debe ser de tipo JSONLike[ScheduleJobParams]",
    ScriptField.SCHEDULE_STATUS: "el estado del script programado debe ser uno de esto valores: 'RUN'|'PAUSE'|'REMOVED'"
}

MSG_WARN_SCRIPTS: dict[T_IDMSG, str] = {
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
    ScriptField.DESCRIPTION: "se recomienda colocar una descripcion al script."
}

class _MetaMsgScripts(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(ScriptField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_SCRIPTS
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_SCRIPTS
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgScripts(metaclass=_MetaMsgScripts):
    """Base para los mensajes de los errores en los campos de las facturas."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_SCRIPTS:
            msg = MSG_EXCEP_SCRIPTS[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_SCRIPTS:
            msg = MSG_WARN_SCRIPTS[id_msg]
        else:
            msg = f"en el campo '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"en el campo '{id_msg}' {msg}"
        if index:
            self.message += f", en los siguientes indices: {index}"
        super().__init__(self.message)

class ScriptsException(_BaseMsgScripts, Exception):
    """Excepciones en los campos de las facturas."""
    msg_type = "exception"

class ScriptsWarning(_BaseMsgScripts, Warning):
    """Advertencias en los campos de las facturas."""
    msg_type = "warning"


class NoMatchScriptFieldsWarning(ScriptsException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class IncorrectScriptFieldsWarning(ScriptsWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
