"""Modulo para la definicion de los campos de la funcionalidad de facturas de compra."""

from typing import TypedDict, TypeGuard
from enum import StrEnum

class BillField(StrEnum):
    """Nombre de las columnas de las facturas de compra de la api Dynamics 365."""
    ID_INTEGRACION = "id_integracion"
    NUMERO_FACTURA = "numero_factura"
    FECHA_FACTURA = "fecha_factura"
    TIENDA = "tienda"
    ALMACEN_TIENDA = "almacen_tienda"
    PROVEEDOR = "proveedor"
    EAN = "ean"
    CANTIDAD = "cantidad"
    COSTO_COMPRA = "costo_compra"
    MONEDA = "moneda"
    FACTURA = "factura"

class BillLine(TypedDict):
    """Estructura de una linea de factura de compra """
    id_integracion: str
    numero_factura: str
    fecha_factura: str
    tienda: str
    almacen_tienda: str
    proveedor: str
    ean: str
    cantidad: str
    costo_compra: str
    moneda: str
    factura: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["BillLine"]:
        """Comprueba de que el objecto sea tipo `BillLine`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("id_integracion"), str),
            isinstance(obj.get("numero_factura"), str),
            isinstance(obj.get("fecha_factura"), str),
            isinstance(obj.get("tienda"), str),
            isinstance(obj.get("almacen_tienda"), str),
            isinstance(obj.get("proveedor"), str),
            isinstance(obj.get("ean"), str),
            isinstance(obj.get("cantidad"), str),
            isinstance(obj.get("costo_compra"), str),
            isinstance(obj.get("moneda"), str),
            isinstance(obj.get("factura"), str),
        ))
