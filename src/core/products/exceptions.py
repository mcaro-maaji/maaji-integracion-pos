"""Modulo de exepciones y advertencias personalizadas para la funcionalidad de productos."""

from typing import Literal
from enum import StrEnum
from .fields import ProductField

class IDMSG(StrEnum):
    """IDs para identificar mensajes de errores."""
    NO_MATCH_FIELDS = "NO_MATCH_FIELDS"
    INCORRECT_FIELDS = "INCORRECT_FIELDS"

T_IDMSG = ProductField | IDMSG

MSG_EXCEP_Products: dict[T_IDMSG, str] = {
    IDMSG.NO_MATCH_FIELDS: "no se encuentran los campos",
    ProductField.ID_INTEGRACION: "el id de integracion no es valido, debe ser 'ZCAM1'",
    ProductField.SKU: "no debe estar vacio",
    ProductField.PROVEEDOR: "no se reconoce el proveedor del producto",
    ProductField.EAN: "no debe estar vacio"
}

MSG_WARN_Products: dict[T_IDMSG, str] = {
    IDMSG.INCORRECT_FIELDS: "estos campos no son necesarios",
    ProductField.FECHA_CREACION_PRODUCTO: "el formato de fecha debe ser 'yyyy-mm-dd'",
    ProductField.FECHA_CREACION: "el formato de fecha debe ser 'yyyy-mm-dd'"
}

class _MetaMsgProducts(type):
    """Meta clase para definir cuales son los campos de los msg tipo exceptiones y advertencias."""

    def __contains__(cls, item):
        is_id_msg = item in list(IDMSG) or item in list(ProductField)
        is_excep = cls.msg_type == "exception" and item in MSG_EXCEP_Products
        is_warn = cls.msg_type == "warning" and item in MSG_WARN_Products
        return is_id_msg and (is_excep | is_warn)

class _BaseMsgProducts(metaclass=_MetaMsgProducts):
    """Base para los mensajes de los errores en los campos de los productos."""
    msg_type: Literal["exception", "warning"]
    id_msg: IDMSG
    index: list[str | int]
    message: str

    def __init__(self, id_msg: T_IDMSG, index: list[str | int]):
        if self.msg_type == "exception" and id_msg in MSG_EXCEP_Products:
            msg = MSG_EXCEP_Products[id_msg]
        elif self.msg_type == "warning" and id_msg in MSG_WARN_Products:
            msg = MSG_WARN_Products[id_msg]
        else:
            msg = f"en el campo '{id_msg}' no se clasifica como un '{self.__class__.__name__}'"
            raise IndexError(msg)

        self.id_msg = id_msg
        self.index = index
        self.message = f"en el campo '{id_msg}' {msg}"
        if index:
            self.message += f", en los siguientes indices: {index}"
        super().__init__(self.message)

class ProductsException(_BaseMsgProducts, Exception):
    """Excepciones en los campos de los productos."""
    msg_type = "exception"

class ProductsWarning(_BaseMsgProducts, Warning):
    """Advertencias en los campos de los productos."""
    msg_type = "warning"


class NoMatchProductFieldsWarning(ProductsException):
    """Excepcion de los campos que hacen falta en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.NO_MATCH_FIELDS, fields)

class IncorrectProductFieldsWarning(ProductsWarning):
    """Advertencia de los campos que estan sobrando en la data."""
    def __init__(self, fields: list[str]):
        super().__init__(IDMSG.INCORRECT_FIELDS, fields)
