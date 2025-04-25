"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de clientes."""

from typing import Literal
from enum import StrEnum
from .fields import ClientField

WARNING_MAX_CLIENTS = 100

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    MAX_CLIENTS = "MAX_CLIENTS"
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = ClientField | IDMSG

__MSG_TIPOS_IDENTIFICACION = "['CC', 'PA', 'CE', 'IE', 'NI', 'TI', 'TE', 'TEL', 'SI']"

MSG_EXCEP_CLIENTS: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    ClientField.TIPOIDENTIFICACION: "solo se admiten estos valores " + __MSG_TIPOS_IDENTIFICACION,
    ClientField.NUMERODOCUMENTO: "no puede ser vacio",
    ClientField.CODIGOPOSTAL: "codigo postal invalido",
    ClientField.FORMULADIRECCION: "no puede ser vacio, por defecto 'CALLE'",
    ClientField.FORMULADIRECCIONMM: "no puede ser vacio, por defecto 'CALLE'",
    ClientField.FECHADENACIMIENTO: "se recomienda colocar la fecha, valor por defecto '00/00/1900'",
    ClientField.FECHADECREACION: "se recomienda colocar la fecha, valor por defecto '00/00/1900'",
    ClientField.PAIS: "solo se admite el valor '169'",
    ClientField.DEPARTAMENTO: "codigo postal invalido",
    ClientField.DIVISA: "solo se admite el valor 'COP'",
}

MSG_WARN_CLIENTS: dict[T_IDMSG, str] = {
    IDMSG.MAX_CLIENTS: f"Hay mas de '{WARNING_MAX_CLIENTS}' clientes, puede fallar la integracion.",
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
    ClientField.NOMBRERAZONSOCIAL: "se recomienda colocar el nombre al cliente",
    ClientField.NOMBRE2: "se recomienda colocar el segundo nombre al cliente",
    ClientField.APELLIDO1: "se recomienda colocar el apellido al cliente",
    ClientField.APELLIDO2: "se recomienda colocar el segundo apellido al cliente",
    ClientField.SEXO: "solo se admiten estos valores ['F', 'M']",
    ClientField.CLIENTE: "solo se admite el valor equis 'X'",
    ClientField.TELEFONO1: "se recomienda colocar el numero telefono al cliente",
    ClientField.TELEFONOMOVIL: "se recomienda colocar el numero telefono celular al cliente",
    ClientField.CORREOCONTACTO: "se recomienda colocar el correo electronico al cliente",
    ClientField.ESTADO: "solo se admite el valor 'ACTIVO'",
    ClientField.REGIMENVENTAS: "solo se admite el valor 'SIMPLIFICADO'",
    ClientField.CODIGONATURALEZAJURIDICA: "solo se admite el valor '2'",
    ClientField.CODIGOACTIVIDADECONOMICA: "solo se admite el valor '0010'",
    ClientField.CODIGOCLASIFICACIONRENTA: "solo se admite el valor 'PND'",
    ClientField.CARGOCONTACTO: "solo se admite el valor 'CLIENTE'",
    ClientField.FACTURACIONELECTRONICACONTACTO: "solo se admite el valor equis 'X'",
}

class _MetaMsgClients(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(ClientField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_CLIENTS
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_CLIENTS
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgClients(metaclass=_MetaMsgClients):
    """Base para los mensajes de los errores en los campos de los clientes."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_CLIENTS:
            msg = MSG_EXCEP_CLIENTS[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_CLIENTS:
            msg = MSG_WARN_CLIENTS[id_msg]
        else:
            msg = f"El ID '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"ID '{id_msg}', {msg}"
        if index:
            self.message += f", en las siguientes indices: {index}"
        super().__init__(self.message)

class ClientsException(_BaseMsgClients, Exception):
    """Excepciones en los campos de los clientes."""
    msg_type = "exception"

class ClientsWarning(_BaseMsgClients, Warning):
    """Advertencias en los campos de los clientes."""
    msg_type = "warning"


class NoMatchClientFieldsWarning(ClientsException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class MaxClientsWarning(ClientsWarning):
    """Advertencia sobre la cantidad maxima de clientes soportados por la integracion."""
    def __init__(self):
        super().__init__(IDMSG.MAX_CLIENTS, [])

class IncorrectClientFieldsWarning(ClientsWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
