"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de facturas."""

from typing import Literal
from enum import StrEnum
from .fields import BillField

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = BillField | IDMSG

MSG_EXCEP_Bills: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    BillField.ID_INTEGRACION: "el id de integracion no es valido, debe ser 'ZENM1'",
    BillField.NUMERO_FACTURA: "el numero de factura debe tener el prefijo 'FEV'",
    BillField.PROVEEDOR: "no se reconoce el proveedor de la factura",
    BillField.TIENDA: "no se reconoce el codigo de la tienda",
    BillField.ALMACEN_TIENDA: "no se reconoce el codigo del almacen de la tienda",
    BillField.EAN: "el codigo de barras del producto no puede ser vacio",
    BillField.CANTIDAD: "la cantidad de producto no puede ser cero",
    BillField.COSTO_COMPRA: "el precio de compra del producto no debe ser cero",
    BillField.MONEDA: "la moneda no es valida, debe ser 'COP'"
}

MSG_WARN_Bills: dict[T_IDMSG, str] = {
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
    BillField.FECHA_FACTURA: "el formato de fecha debe ser 'yyyy-mm-dd'",
    BillField.FACTURA: "los digitos de la factura no coinciden con el numero de factura"
}

class _MetaMsgBills(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(BillField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_Bills
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_Bills
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgBills(metaclass=_MetaMsgBills):
    """Base para los mensajes de los errores en los campos de las facturas."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_Bills:
            msg = MSG_EXCEP_Bills[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_Bills:
            msg = MSG_WARN_Bills[id_msg]
        else:
            msg = f"en el campo '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"en el campo '{id_msg}' {msg}"
        if index:
            self.message += f", en los siguientes indices: {index}"
        super().__init__(self.message)

class BillsException(_BaseMsgBills, Exception):
    """Excepciones en los campos de las facturas."""
    msg_type = "exception"

class BillsWarning(_BaseMsgBills, Warning):
    """Advertencias en los campos de las facturas."""
    msg_type = "warning"


class NoMatchBillFieldsWarning(BillsException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class IncorrectBillFieldsWarning(BillsWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
