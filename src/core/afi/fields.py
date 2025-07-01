"""Modulo para la definicion de los campos de la funcionalidad de interfaz contable."""

from typing import TypedDict, TypeGuard, Literal
from enum import StrEnum

class AFIField(StrEnum):
    """Nombre de las columnas de la interfaz contable."""
    CODIGO_DOCUMENTO = "Codigo Documento"
    TERCERO_PRINCIPAL = "Tercero Principal"
    PREFIJO = "Prefijo"
    NUMERO = "Numero"
    SUFIJO = "Sufijo"
    FECHA_ELABORACION = "Fecha Elaboracion"
    CODIGO_MONEDA = "Codigo Moneda"
    TASA_DE_CAMBIO = "Tasa de Cambio"
    CUENTA_CONTABLE = "Cuenta Contable"
    NIT_TERCERO_PRINCIAPL = "Nit/Codigo Tercero"
    CODIGO_CENTRO_COSTOS = "Codigo Centro Costos"
    BASE_DE_IMPUESTOS = "Base de Impuestos"
    DEBITOS = "Debitos"
    CREDITOS = "Creditos"
    BASE_DE_IMPUESTOS_NIIF = "Base NIIF de Impuestos"
    DEBITOS_NIIF = "Debitos NIIF"
    CREDITOS_NIIF = "Creditos NIIF"
    OBSERVACION_DETALLE = "Observacion Detalle"
    OBSERVACIONES_MOVIMIENTO = "Observaciones Movimiento"

class AFILine(TypedDict):
    """Estructura de una linea de la interfaz contable"""
    codigo_documento: str
    tercero_principal: str
    prefijo: str
    numero: str
    sufijo: str
    fecha_elaboracion: str
    codigo_moneda: str
    cuenta_contable: str
    nit_codigo_tercero: str
    base_de_impuestos: str
    debitos: str
    creditos: str
    base_niif_de_impuestos: str
    debitos_niif: str
    creditos_niif: str
    observacion_detalle: str
    observaciones_movimiento: str

    @classmethod
    def validate(cls, obj) -> TypeGuard["AFILine"]:
        """Comprueba de que el objecto sea tipo `AFILine`"""
        if not isinstance(obj, dict):
            return False
        return all((
            isinstance(obj.get("codigo_documento"), str),
            isinstance(obj.get("tercero_principal"), str),
            isinstance(obj.get("prefijo"), str),
            isinstance(obj.get("numero"), str),
            isinstance(obj.get("sufijo"), str),
            isinstance(obj.get("fecha_elaboracion"), str),
            isinstance(obj.get("codigo_moneda"), str),
            isinstance(obj.get("cuenta_contable"), str),
            isinstance(obj.get("nit_codigo_tercero"), str),
            isinstance(obj.get("base_de_impuestos"), str),
            isinstance(obj.get("debitos"), str),
            isinstance(obj.get("creditos"), str),
            isinstance(obj.get("base_niif_de_impuestos"), str),
            isinstance(obj.get("debitos_niif"), str),
            isinstance(obj.get("creditos_niif"), str),
            isinstance(obj.get("observacion_detalle"), str),
            isinstance(obj.get("observaciones_movimiento"), str),
        ))


class AFIParameterField(StrEnum):
    """Nombre de las columnas de los parametros de la interfaz contable."""
    MOVIMIENTO = "Movimiento"
    CODIGO_TIENDA = "Codigo Tienda"
    COMPROBANTE = "Comprobante"
    SOUCHE = "Souche"
    MODO_PAGO = "Modo Pago"
    FRANQUICIA = "Franquicia"
    CUENTA = "Cuenta"
    NATURALEZA = "Naturaleza"
    NIT = "Nit"
    FACTOR = "Factor"
    CECO = "CECO"


AFIMovimento = Literal[
    "Ajuste de Entrada",
    "Ajuste de Salida",
    "Egresos",
    "Factura de Compra",
    "Devolucion de Compra",
    "Factura de Venta",
    "Nota Credito",
    "Devolucion Ecommerce",
    "Ingreso",
    "Recepcion de Compra",
    "Transferencia"
]

AFIValorNaturaleza = Literal["Debito", "Credito"]

class AFITransferField(StrEnum):
    """Nombre de las columnas de las transferencias de la interfaz contable."""
    CLASE = "Clase"
    NUMERO = "Numero"
    FECHA_TRANSFERENCIA = "Fecha transferencia"
    ALMACEN_EMISOR = "Almacen Emisor"
    ALMACEN_DESTINATARIO = "Almacen Destinatario"
    ESTABLECIMIENTO_EMISOR = "Establecimiento del doc."
    ESTABLECIMIENTO_DESTINATARIO = "Establecimiento destinatario"
