"""Modulo para la lectura, analisis y correccion de los precios."""

from datetime import datetime
from pandas import Series, Index, MultiIndex, to_datetime
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from utils.constants import TZ_LOCAL
from .fields import PriceField
from .exceptions import (
    PricesException,
    PricesWarning,
    NoMatchPriceFieldsWarning,
    IncorrectPriceFieldsWarning,
)

class Prices(BaseDataIO):
    """Clase para la gestion de datos de los precios."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de los precios."""
        super().__init__(source, destination, support, mode)

        header = kwargs.pop("header", "no defined")
        if support != "json" and header is None and "names" not in kwargs:
            kwargs["names"] = list(PriceField)

        self.load(dtype=str, **kwargs)
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in PriceField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(PriceField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[PriceField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(PriceField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[PriceField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def normalize(self):
        """
        Aplica en los datos los siguientes puntos:
            - Renovar Id Integracion.
            - Corrige fecha al formato '%m/%d/%Y %I:%M:%S %p' -> ISO.
            - El costo de String:,.2f a tipo Decimal
            - Ordena los datos por la fecha de modificacion
        """
        id_integracion = self.data[PriceField.ID_INTEGRACION]
        id_integracion = id_integracion.str.replace(r"(\s|I|R)$", "", regex=True) + " "
        self.data[PriceField.ID_INTEGRACION] = id_integracion

        def format_date(value: str):
            try:
                date = datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                try:
                    date = datetime.fromisoformat(value)
                except ValueError:
                    return value
            return date.astimezone(TZ_LOCAL).isoformat()

        fecha_modificacion = self.data[PriceField.FECHA_MODIFICACION]
        fecha_modificacion = fecha_modificacion.apply(format_date)
        self.data[PriceField.FECHA_MODIFICACION] = fecha_modificacion

        precio = self.data[PriceField.PRECIO]
        precio = precio.str.replace(",", "", regex=False)
        precio = precio.astype(float).apply(lambda num: f"{num:.2f}").astype(str)
        self.data[PriceField.PRECIO] = precio

        self.data = self.data.sort_values(by=PriceField.FECHA_MODIFICACION)

    def analyze(self):
        """Analiza los datos y devuelve los erroes encontrados."""

        id_integracion = self.data[PriceField.ID_INTEGRACION]
        id_integracion = id_integracion[~id_integracion.str.startswith("ZPRM1")]

        moneda = self.data[PriceField.MONEDA]
        moneda = moneda[moneda != "COP"]

        codigo = self.data[PriceField.CODIGO]
        codigo = codigo[codigo == ""]

        ean = self.data[PriceField.EAN]
        ean = ean[ean == ""]

        precio = self.data[PriceField.PRECIO]
        precio = precio[precio.isin(["", "0", "0.", "0.0", "0.00"])]

        def is_date(value: str):
            try:
                datetime.fromisoformat(value)
                return True
            except ValueError:
                return False

        if PriceField.FECHA_MODIFICACION in self.data:
            fecha_modificacion = self.data[PriceField.FECHA_MODIFICACION]
            fecha_modificacion = fecha_modificacion[~fecha_modificacion.apply(is_date)]
            fecha_modificacion_index = fecha_modificacion.index
        else:
            fecha_modificacion_index = []

        return {
            PriceField.ID_INTEGRACION: id_integracion.index,
            PriceField.MONEDA: moneda.index,
            PriceField.CODIGO: codigo.index,
            PriceField.EAN: ean.index,
            PriceField.PRECIO: precio.index,
            PriceField.FECHA_MODIFICACION: fecha_modificacion_index,
        }

    def filter_fecha_modificacion(self, date_start: datetime, date_end: datetime = None):
        """Filtra los datos por un rango de fecha especifico."""

        fecha_modificacion = to_datetime(self.data[PriceField.FECHA_MODIFICACION], utc=False)
        self.data[PriceField.FECHA_MODIFICACION] = fecha_modificacion

        self.data = self.data.sort_values(by=PriceField.FECHA_MODIFICACION)
        fecha_modificacion = self.data[PriceField.FECHA_MODIFICACION]
        last_fecha_modificacion = fecha_modificacion.iloc[-1]

        if date_end is None:
            date_end = last_fecha_modificacion

        date_start = date_start.astimezone(TZ_LOCAL)
        date_end = date_end.astimezone(TZ_LOCAL)

        date_filter = (fecha_modificacion >= date_start) & (fecha_modificacion <= date_end)
        self.data = self.data[date_filter]

        fecha_modificacion = self.data[PriceField.FECHA_MODIFICACION]
        iso_format = '%Y-%m-%dT%H:%M:%S%z'
        self.data[PriceField.FECHA_MODIFICACION] = fecha_modificacion.dt.strftime(iso_format)

    def fullfix(self, date_start: datetime, date_end: datetime = None):
        """Ejecuta la auto reparacion de los datos de los precios."""
        self.normalize()
        self.sort_fields()
        self.filter_fecha_modificacion(date_start, date_end)
        return self.analyze()

    def exceptions(self, analysis: dict[PriceField, Index | MultiIndex]):
        """Obtiene todos los errores y los mensajes propios por cada campo de los precios."""
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [PricesException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in PricesException and len(idx) > 0]

        fields_warnings = [PricesWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in PricesWarning and len(idx) > 0]

        return (
            NoMatchPriceFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectPriceFieldsWarning(incorrect_fields) if incorrect_fields else None,
            *fields_exceptions,
            *fields_warnings
        )
