"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de precios."""

from typing import Literal
from enum import StrEnum
from .fields import PriceField

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = PriceField | IDMSG

MSG_EXCEP_Prices: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    PriceField.ID_INTEGRACION: "el id de integracion no es valido, debe ser 'ZENM1'",
    PriceField.MONEDA: "la moneda no es valida, debe ser 'COP'",
    PriceField.CODIGO: "el codigo no puede ser vacio",
    PriceField.EAN: "el codigo de barras no puede ser vacio",
    PriceField.FECHA_MODIFICACION: "el formato debe ser 'mm/dd/yyyy HH:MM:SS am|pm'"
}

MSG_WARN_Prices: dict[T_IDMSG, str] = {
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
}

class _MetaMsgPrices(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(PriceField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_Prices
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_Prices
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgPrices(metaclass=_MetaMsgPrices):
    """Base para los mensajes de los errores en los campos de los precios."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_Prices:
            msg = MSG_EXCEP_Prices[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_Prices:
            msg = MSG_WARN_Prices[id_msg]
        else:
            msg = f"en el campo '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"en el campo '{id_msg}' {msg}"
        if index:
            self.message += f", en los siguientes indices: {index}"
        super().__init__(self.message)

class PricesException(_BaseMsgPrices, Exception):
    """Excepciones en los campos de los precios."""
    msg_type = "exception"

class PricesWarning(_BaseMsgPrices, Warning):
    """Advertencias en los campos de los precios."""
    msg_type = "warning"


class NoMatchPriceFieldsWarning(PricesException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class IncorrectPriceFieldsWarning(PricesWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
