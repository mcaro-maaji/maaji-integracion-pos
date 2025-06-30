"""Modulo para la lectura, analisis y correccion de las facturas de compra."""

from datetime import datetime
from pandas import Series, Index, MultiIndex
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from core.stores import STORES, StoreField
from core.providers import PROVIDERS, ProviderField
from .fields import BillField
from .exceptions import (
    BillsException,
    BillsWarning,
    NoMatchBillFieldsWarning,
    IncorrectBillFieldsWarning,
)

class Bills(BaseDataIO):
    """Clase para la gestion de datos de las facturas de compra."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de las facturas."""
        super().__init__(source, destination, support, mode)
        self.load(dtype=str, **kwargs)
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in BillField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(BillField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[BillField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(BillField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[BillField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def normalize(self):
        """
        Aplica en los datos los siguientes puntos:
            - Renovar Id Integracion.
            - Corrige fecha al formato '%Y-%m-%d'.
            - La cantidad de tipo String:.2f a Entero.
            - El costo de String:,.2f a tipo Decimal
            - En la factura retirar el prefijo, ej 'FEV'
            - Ordena los datos por el numero de factura
        """
        id_integracion = self.data[BillField.ID_INTEGRACION]
        id_integracion = id_integracion.str.replace(r"(\s|I|R)$", " ", regex=True)
        self.data[BillField.ID_INTEGRACION] = id_integracion

        def format_date(value: str):
            try:
                date = datetime.strptime(value, "%m/%d/%Y")
            except ValueError:
                try:
                    date = datetime.fromisoformat(value)
                except ValueError:
                    return value
            return date.strftime("%Y-%m-%d")

        fecha_factura = self.data[BillField.FECHA_FACTURA]
        fecha_factura = fecha_factura.apply(format_date)
        self.data[BillField.FECHA_FACTURA] = fecha_factura

        cantidad = self.data[BillField.CANTIDAD]
        cantidad = cantidad.astype(float).astype(int).astype(str)
        self.data[BillField.CANTIDAD] = cantidad

        costo_compra = self.data[BillField.COSTO_COMPRA]
        costo_compra = costo_compra.str.replace(",", "", regex=False)
        costo_compra = costo_compra.astype(float).apply(lambda num: f"{num:.2f}").astype(str)
        self.data[BillField.COSTO_COMPRA] = costo_compra

        numero_factura = self.data[BillField.NUMERO_FACTURA]
        factura = numero_factura.str.replace(r"^[A-Za-z]+", "", regex=True)
        self.data[BillField.FACTURA] = factura

        self.data = self.data.sort_values(by=BillField.NUMERO_FACTURA)

    def analyze(self):
        """Analiza los datos y devuelve los erroes encontrados."""

        id_integracion = self.data[BillField.ID_INTEGRACION]
        id_integracion = id_integracion[~id_integracion.str.startswith("ZENM1")]

        df_numero_factura = self.data[BillField.NUMERO_FACTURA]
        numero_factura = df_numero_factura[~df_numero_factura.str.startswith("FEV")]

        def is_date(value: str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except ValueError:
                return False

        fecha_factura = self.data[BillField.FECHA_FACTURA]
        fecha_factura = fecha_factura[~fecha_factura.apply(is_date)]

        tienda = self.data[BillField.TIENDA]
        tienda = tienda[~tienda.isin(STORES[StoreField.CODIGO_TIENDA])]

        almacen = self.data[BillField.ALMACEN_TIENDA]
        almacen = almacen[~almacen.isin(STORES[StoreField.CODIGO_ALMACEN])]

        proveedor = self.data[BillField.PROVEEDOR]
        proveedor = proveedor[~proveedor.isin(PROVIDERS[ProviderField.CODIGO])]

        ean = self.data[BillField.EAN]
        ean = ean[ean == ""]

        cantidad = self.data[BillField.CANTIDAD]
        cantidad = cantidad[cantidad.isin(["", "0", "0.", "0.0", "0.00"])]

        costo = self.data[BillField.COSTO_COMPRA]
        costo = costo[costo.isin(["", "0", "0.", "0.0", "0.00"])]

        moneda = self.data[BillField.MONEDA]
        moneda = moneda[moneda == "COP"]

        factura = self.data[BillField.FACTURA]
        factura = factura[factura == df_numero_factura.replace("FEV", "", regex=False)]

        return {
            BillField.ID_INTEGRACION: id_integracion.index,
            BillField.NUMERO_FACTURA: numero_factura.index,
            BillField.FECHA_FACTURA: fecha_factura.index,
            BillField.TIENDA: tienda.index,
            BillField.ALMACEN_TIENDA: almacen.index,
            BillField.PROVEEDOR: proveedor.index,
            BillField.EAN: ean.index,
            BillField.CANTIDAD: cantidad.index,
            BillField.COSTO_COMPRA: costo.index,
            BillField.MONEDA: moneda.index,
            BillField.FACTURA: factura.index
        }

    def fullfix(self):
        """Ejecuta la auto reparacion de los datos de las facturas."""
        self.normalize()
        self.sort_fields()
        return self.analyze()

    def exceptions(self, analysis: dict[BillField, Index | MultiIndex]):
        """Obtiene todos los errores y los mensajes propios por cada campo de las facturas."""
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [BillsException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in BillsException and len(idx) > 0]

        fields_warnings = [BillsWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in BillsWarning and len(idx) > 0]

        return (
            NoMatchBillFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectBillFieldsWarning(incorrect_fields) if incorrect_fields else None,
            *fields_exceptions,
            *fields_warnings
        )
