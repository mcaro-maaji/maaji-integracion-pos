"""Modulo para la lectura, analisis y correccion de los productos."""

from datetime import datetime
from pandas import Series, Index, MultiIndex
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from core.providers import PROVIDERS, ProviderField
from .fields import ProductField
from .exceptions import (
    ProductsException,
    ProductsWarning,
    NoMatchProductFieldsWarning,
    IncorrectProductFieldsWarning,
)

class Products(BaseDataIO):
    """Clase para la gestion de datos de los productos."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de los productos."""
        super().__init__(source, destination, support, mode)
        self.load(dtype=str, **kwargs)
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in ProductField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(ProductField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[ProductField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(ProductField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[ProductField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def normalize(self):
        """
        Aplica en los datos los siguientes puntos:
            - Renovar Id Integracion.
            - Retira el cero del codigo de barras para obtener el EAN.
            - Corrige fecha al formato '%Y-%m-%d'.
            - Ordena los datos por el SKU
        """
        id_integracion = self.data[ProductField.ID_INTEGRACION]
        id_integracion = id_integracion.str.replace(r"(\s|I|R)$", "", regex=True) + " "
        self.data[ProductField.ID_INTEGRACION] = id_integracion

        ean = self.data[ProductField.EAN]
        ean = ean.str.replace(r"^0", "", regex=True)
        self.data[ProductField.EAN] = ean

        def format_date(value: str):
            try:
                date = datetime.strptime(value, "%m/%d/%Y")
            except ValueError:
                try:
                    date = datetime.fromisoformat(value)
                except ValueError:
                    return value
            return date.strftime("%Y-%m-%d")

        fecha_creacion_producto = self.data[ProductField.FECHA_CREACION_PRODUCTO]
        fecha_creacion_producto = fecha_creacion_producto.apply(format_date)
        self.data[ProductField.FECHA_CREACION_PRODUCTO] = fecha_creacion_producto

        fecha_creacion = self.data[ProductField.FECHA_CREACION]
        fecha_creacion = fecha_creacion.apply(format_date)
        self.data[ProductField.FECHA_CREACION] = fecha_creacion

        self.data = self.data.sort_values(by=ProductField.SKU)

    def analyze(self):
        """Analiza los datos y devuelve los erroes encontrados."""

        id_integracion = self.data[ProductField.ID_INTEGRACION]
        id_integracion = id_integracion[~id_integracion.str.startswith("ZCAM1")]

        sku = self.data[ProductField.SKU]
        sku = sku[sku == ""]

        referencia = self.data[ProductField.REFERENCIA]
        referencia = referencia[referencia == ""]

        ean = self.data[ProductField.EAN]
        ean = ean[ean == ""]

        proveedor = self.data[ProductField.PROVEEDOR]
        proveedor = proveedor[~proveedor.isin(PROVIDERS[ProviderField.CODIGO])]
        def is_date(value: str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except ValueError:
                return False

        fecha_creacion_producto = self.data[ProductField.FECHA_CREACION_PRODUCTO]
        fecha_creacion_producto = fecha_creacion_producto[~fecha_creacion_producto.apply(is_date)]

        fecha_creacion = self.data[ProductField.FECHA_CREACION]
        fecha_creacion = fecha_creacion[~fecha_creacion.apply(is_date)]

        return {
            ProductField.ID_INTEGRACION: id_integracion.index,
            ProductField.SKU: sku.index,
            ProductField.EAN: ean.index,
            ProductField.PROVEEDOR: proveedor.index,
            ProductField.FECHA_CREACION_PRODUCTO: fecha_creacion_producto.index,
            ProductField.FECHA_CREACION: fecha_creacion.index
        }

    def fullfix(self):
        """Ejecuta la auto reparacion de los datos de los productos."""
        self.normalize()
        self.sort_fields()
        return self.analyze()

    def exceptions(self, analysis: dict[ProductField, Index | MultiIndex]):
        """Obtiene todos los errores y los mensajes propios por cada campo de los productos."""
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [ProductsException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in ProductsException and len(idx) > 0]

        fields_warnings = [ProductsWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in ProductsWarning and len(idx) > 0]

        return (
            NoMatchProductFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectProductFieldsWarning(incorrect_fields) if incorrect_fields else None,
            *fields_exceptions,
            *fields_warnings
        )
