"""Modulo para la definicion de los campos de la funcionalidad de precios."""

from typing import TypedDict, TypeGuard
from enum import StrEnum

class PriceField(StrEnum):
    """Nombre de las columnas de los precios de la api Dynamics 365."""
    ID_INTEGRACION = "id"
    MONEDA = "moneda"
    CODIGO = "codigo"
    EAN = "ean"
    PRECIO = "copRP"
    FECHA_MODIFICACION = "fecha_modificacion"

class PriceLine(TypedDict):
    """Estructura de una linea de factura de compra """
    id: str
    moneda: str
    codigo: str
    ean: str
    copRP: str
    fecha_modificacion: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["PriceLine"]:
        """Comprueba de que el objecto sea tipo `PriceLine`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("id"), str),
            isinstance(obj.get("moneda"), str),
            isinstance(obj.get("codigo"), str),
            isinstance(obj.get("ean"), str),
            isinstance(obj.get("copRP"), str),
            isinstance(obj.get("fecha_modificacion"), str)
        ))
