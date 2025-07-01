"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de interfaz contable."""

from typing import Literal
from enum import StrEnum
from .fields import AFIField

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = AFIField | IDMSG

MSG_EXCEP_AFI: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    AFIField.CODIGO_DOCUMENTO: "no se reconoce el codigo del documento en los parametros IC",
    AFIField.CUENTA_CONTABLE: "no se reconoce la cuenta contable en los parametros IC",
    AFIField.CODIGO_CENTRO_COSTOS: "no se reconoce el centro de costos en los parametros IC",
    AFIField.NUMERO: "debe ser un valor numerico entero",
    AFIField.FECHA_ELABORACION: "el formato de fecha debe ser 'yyyy-mm-dd'",
    AFIField.DEBITOS: "debe ser un valor numerico entero",
    AFIField.CREDITOS: "debe ser un valor numerico entero",
    AFIField.OBSERVACION_DETALLE: "no puede ser vacio",
}

MSG_WARN_AFI: dict[T_IDMSG, str] = {
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
    AFIField.TERCERO_PRINCIPAL: "se recomienda rellenar con un valor",
    AFIField.OBSERVACIONES_MOVIMIENTO: "se recomienda rellenar con un valor"
}

class _MetaMsgAFI(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(AFIField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_AFI
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_AFI
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgAFI(metaclass=_MetaMsgAFI):
    """Base para los mensajes de los errores en los campos de las facturas."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_AFI:
            msg = MSG_EXCEP_AFI[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_AFI:
            msg = MSG_WARN_AFI[id_msg]
        else:
            msg = f"en el campo '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"en el campo '{id_msg}' {msg}"
        if index:
            self.message += f", en los siguientes indices: {index}"
        super().__init__(self.message)

class AFIException(_BaseMsgAFI, Exception):
    """Excepciones en los campos de las facturas."""
    msg_type = "exception"

class AFIWarning(_BaseMsgAFI, Warning):
    """Advertencias en los campos de las facturas."""
    msg_type = "warning"


class NoMatchAFIFieldsWarning(AFIException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class IncorrectAFIFieldsWarning(AFIWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
