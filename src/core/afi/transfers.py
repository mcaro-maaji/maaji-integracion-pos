"""Modulo para la lectura, de las transferencias en interfaz contable"""

from datetime import datetime
from pandas import Series
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from core.stores import STORES_REFUND_ZF, StoreField
from .fields import AFITransferField

class AFITransfers(BaseDataIO):
    """Clase para la gestion de datos de las transferencias de interfaz contable."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de las transferencias."""
        super().__init__(source, destination, support, mode)
        self.load(dtype=str, **kwargs)
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in AFITransferField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(AFITransferField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[AFITransferField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(AFITransferField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[AFITransferField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def normalize(self):
        """
        Aplica en los datos los siguientes puntos:
            - Elimina las transferencias que no son requeridas.
            - Corrige el formato de fecha 'dd/mm/yyyy' -> 'yyyy/mm/dd'
            - Ordena los datos por la fecha de transferencia.
        """
        stores_refund_codigos = STORES_REFUND_ZF[StoreField.CODIGO_TIENDA]
        establecimiento_dst = self.data[AFITransferField.ESTABLECIMIENTO_DESTINATARIO]
        self.data = self.data[establecimiento_dst.isin(stores_refund_codigos)]

        def format_date(value: str):
            try:
                date = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                try:
                    date = datetime.fromisoformat(value)
                except ValueError:
                    return value
            return date.strftime("%Y/%m/%d")

        fecha_transferencia = self.data[AFITransferField.FECHA_TRANSFERENCIA]
        fecha_transferencia = fecha_transferencia.apply(format_date)
        self.data[AFITransferField.FECHA_TRANSFERENCIA] = fecha_transferencia

        self.data = self.data.sort_values(by=AFITransferField.FECHA_TRANSFERENCIA)

    def fullfix(self):
        """Ejecuta la auto reparacion de los datos de las transferencias."""
        self.normalize()
        self.sort_fields()
        return {}
