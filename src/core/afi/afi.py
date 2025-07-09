"""
Modulo para la lectura, analisis y correccion de interfaz contable (Accounting Financial Interface).
"""

from __future__ import annotations
from datetime import datetime
from pandas import Series, Index, MultiIndex
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from .paramters import AFI_PARAMETERS_UNIQUE
from .transfers import AFITransfers
from .fields import AFIField, AFIParameterField, AFITransferField
from .exceptions import (
    AFIException,
    AFIWarning,
    NoMatchAFIFieldsWarning,
    IncorrectAFIFieldsWarning,
)

class AFI(BaseDataIO):
    """Clase para la gestion de datos de la interfaz contable."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de la interfaz contable."""
        super().__init__(source, destination, support, mode)

        header = kwargs.pop("header", "no defined")
        if support != "json" and header is None and "names" not in kwargs:
            kwargs["names"] = list(AFIField)

        self.load(dtype=str, **kwargs)
        self.data.fillna("", inplace=True)
        self.data_src = self.data.copy()

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in AFIField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(AFIField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[AFIField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(AFIField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[AFIField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def set_parameters(self):
        """Agrega los parámetros IC a los datos, retorna las columnas antiguas"""
        old_columns = self.data.columns.copy()

        fields_afi_parameters = [f for f in AFIParameterField if f in AFI_PARAMETERS_UNIQUE.data]
        df_parameters = AFI_PARAMETERS_UNIQUE.data[fields_afi_parameters].copy()

        id_merge_left_on = [
            AFIField.CODIGO_DOCUMENTO,
            AFIField.CUENTA_CONTABLE,
            AFIField.CODIGO_CENTRO_COSTOS
        ]
        id_merge_right_on = [
            AFIParameterField.COMPROBANTE,
            AFIParameterField.CUENTA,
            AFIParameterField.CECO
        ]

        self.data = self.data.merge(
            df_parameters,
            how="left",
            left_on=id_merge_left_on,
            right_on=id_merge_right_on
        )

        return old_columns

    def parameters_is_set(self):
        """Comprueba que existen los parametros en los datos IC"""
        return not all(f not in self.data for f in AFIParameterField)

    def total(self):
        """Obtiene la suma de los debitos y creditos."""
        debitos = self.data[AFIField.DEBITOS].replace("", "0").astype(int).sum()
        creditos = self.data[AFIField.CREDITOS].replace("", "0").astype(int).sum()
        return debitos - creditos

    def groupby(self):
        """Agrupa todos los movimientos."""

        fields_group = [
            AFIField.CODIGO_DOCUMENTO,
            AFIField.NUMERO,
            AFIField.FECHA_ELABORACION,
            AFIField.CODIGO_CENTRO_COSTOS,
        ]

        return self.data.groupby(fields_group)

    def total_groupby(self):
        """Verifica cuales son los movimientos tienen diferencias en debitos y creditos."""
        groups = self.groupby()
        list_diferences: list[tuple[tuple, Index]] = []

        for values, df_group in groups:
            debitos = df_group[AFIField.DEBITOS].replace("", "0").astype(int).sum()
            creditos = df_group[AFIField.CREDITOS].replace("", "0").astype(int).sum()
            diference = debitos - creditos

            if not diference:
                continue

            list_diferences.append((values, df_group.index))

        return list_diferences

    def list_with_ceros(self):
        """Verifica cuales son los movimientos que tienen debitos y creditos con un valor cero."""
        groups = self.groupby()
        list_values_cero: list[tuple[tuple, Index]] = []

        for values, df_group in groups:
            debitos = df_group[AFIField.DEBITOS]
            debitos = debitos[debitos.str.strip() == "0"]
            creditos = df_group[AFIField.CREDITOS]
            creditos = creditos[creditos.str.strip() == "0"]

            if debitos.empty and creditos.empty:
                continue
            list_values_cero.append((values, df_group.index))

        return list_values_cero

    def normalize(self, transfers: AFITransfers = None, valid_duplicates: "AFI" = None):
        """
        Aplica en los datos los siguientes puntos:
            - Corrige los valores en cero.
            - Elimina las transferencias que no deben ir, solo las de devolucion zf.
            - Ordena los datos por el codigo documento, fecha elaboracion, numero.
            - Elimina los movimientos duplicados.
            - Verifica movimientos que ya existen `valid_duplicates`.
            - Elimina los movimientos sin numero.
            - Elimina los movimientos que causan diferencias en debitos y creditos.
            - Elimina los movimientos quee tengan debitos y creditos en ceros.
        Requiere de los parametros de la IC, mirar `AFI.set_parameters`
        """
        if not self.parameters_is_set():
            return

        # Elimina los movimientos sin numero

        numero = self.data[AFIField.NUMERO]
        numero = numero[~numero.str.strip().str.isdigit()]
        self.data.drop(index=numero.index, inplace=True)

        # Corregir los valores en cero, solo para ajustes y transferencias

        movimiento = self.data[AFIParameterField.MOVIMIENTO]
        mov_borrado_cero = ["Ajuste de Entrada", "Ajuste de Salida", "Transferencia"]
        mov_borrado_cero = self.data[movimiento.isin(mov_borrado_cero)]

        deb_mov_borrado_cero = mov_borrado_cero[AFIField.DEBITOS]
        deb_mov_borrado_cero = deb_mov_borrado_cero[deb_mov_borrado_cero == "0"]
        self.data.drop(index=deb_mov_borrado_cero.index, inplace=True)

        cre_mov_borrado_cero = mov_borrado_cero[AFIField.CREDITOS]
        cre_mov_borrado_cero = cre_mov_borrado_cero[cre_mov_borrado_cero == "0"]
        self.data.drop(index=cre_mov_borrado_cero.index, inplace=True)

        # Elimina las transferencias innecesarias

        mov_borrar_transfer = ["Transferencia"]
        movimiento = self.data[AFIParameterField.MOVIMIENTO]
        mov_borrar_transfer = self.data[movimiento.isin(mov_borrar_transfer)]

        if not transfers is None:
            transfers.fullfix()
            id_mov_borrar_transfer = mov_borrar_transfer[AFIParameterField.CODIGO_TIENDA].copy()
            id_mov_borrar_transfer += "|" + mov_borrar_transfer[AFIField.NUMERO]
            id_mov_borrar_transfer += "|" + mov_borrar_transfer[AFIField.FECHA_ELABORACION]

            id_transfer = transfers.data[AFITransferField.ESTABLECIMIENTO_EMISOR]
            id_transfer += "|" + transfers.data[AFITransferField.NUMERO]
            id_transfer += "|" + transfers.data[AFITransferField.FECHA_TRANSFERENCIA]

            filter_transfer = id_mov_borrar_transfer.isin(id_transfer)
            mov_borrar_transfer = mov_borrar_transfer[~filter_transfer]

        self.data.drop(index=mov_borrar_transfer.index, inplace=True)

        fields_no_duplicates = [
            AFIField.CODIGO_DOCUMENTO,
            AFIField.FECHA_ELABORACION,
            AFIField.CUENTA_CONTABLE,
            AFIField.CODIGO_CENTRO_COSTOS,
            AFIField.OBSERVACION_DETALLE,
            AFIField.OBSERVACIONES_MOVIMIENTO,
        ]

        self.data.drop_duplicates(inplace=True, ignore_index=True)
        # self.data.drop_duplicates(fields_no_duplicates, inplace=True, ignore_index=True)

        # verifica los duplicados desde otro set de datos AFI

        if not valid_duplicates is None:
            valid_duplicates.fullfix()

            mask = self.data[fields_no_duplicates].apply(tuple, axis=1)
            mask = mask.isin(valid_duplicates.data[fields_no_duplicates].apply(tuple, axis=1))
            self.data = self.data[~mask]

        # Elimina los movimientos que causan diferencias en debitos y creditos

        list_diferences = self.total_groupby()
        for _, index in list_diferences:
            self.data.drop(index=index, inplace=True)

        # Elimina los movimientos que tengan debitos y creditos en ceros

        list_with_ceros = self.list_with_ceros()
        for _, index in list_with_ceros:
            self.data.drop(index=index, inplace=True)

        # Ordena los datos

        sort_by = [AFIField.CODIGO_DOCUMENTO, AFIField.FECHA_ELABORACION, AFIField.NUMERO]
        self.data.sort_values(by=sort_by, inplace=True)

    def analyze(self):
        """Analiza los datos y devuelve los errores encontrados."""

        id_valid_parameters = self.data[AFIField.CODIGO_DOCUMENTO].copy()
        id_valid_parameters += "|" + self.data[AFIField.CUENTA_CONTABLE]
        id_valid_parameters += "|" + self.data[AFIField.CODIGO_CENTRO_COSTOS]

        id_parameters = AFI_PARAMETERS_UNIQUE.data[AFIParameterField.COMPROBANTE].copy()
        id_parameters += "|" + AFI_PARAMETERS_UNIQUE.data[AFIParameterField.CUENTA]
        id_parameters += "|" + AFI_PARAMETERS_UNIQUE.data[AFIParameterField.CECO]

        no_valid_parameters = id_valid_parameters[~id_valid_parameters.isin(id_parameters)]

        tercero_principal = self.data[AFIField.TERCERO_PRINCIPAL]
        tercero_principal = tercero_principal[tercero_principal == ""]

        numero = self.data[AFIField.NUMERO]
        numero = numero[~numero.str.isdigit()]

        def is_date(value: str):
            try:
                datetime.strptime(value, "%Y/%m/%d")
                return True
            except ValueError:
                return False

        fecha_elaboracion = self.data[AFIField.FECHA_ELABORACION]
        fecha_elaboracion = fecha_elaboracion[~fecha_elaboracion.apply(is_date)]

        debitos = self.data[AFIField.DEBITOS].replace("", "0")
        debitos = debitos[~debitos.str.isdigit()]

        creditos = self.data[AFIField.CREDITOS].replace("", "0")
        creditos = creditos[~creditos.str.isdigit()]

        observacion_detalle = self.data[AFIField.OBSERVACION_DETALLE]
        observacion_detalle = observacion_detalle[observacion_detalle == ""]

        observaciones_movimiento = self.data[AFIField.OBSERVACIONES_MOVIMIENTO]
        observaciones_movimiento = observaciones_movimiento[observaciones_movimiento == ""]

        return {
            AFIField.CODIGO_DOCUMENTO: no_valid_parameters.index,
            AFIField.CUENTA_CONTABLE: no_valid_parameters.index,
            AFIField.CODIGO_CENTRO_COSTOS: no_valid_parameters.index,
            AFIField.TERCERO_PRINCIPAL: tercero_principal.index,
            AFIField.NUMERO: numero.index,
            AFIField.FECHA_ELABORACION: fecha_elaboracion.index,
            AFIField.DEBITOS: debitos.index,
            AFIField.CREDITOS: creditos.index,
            AFIField.OBSERVACION_DETALLE: observacion_detalle.index,
            AFIField.OBSERVACIONES_MOVIMIENTO: observaciones_movimiento.index
        }

    def fullfix(self, transfers: AFITransfers = None, valid_duplicates: "AFI" = None):
        """Ejecuta la auto reparacion de los datos de la interfaz contable."""
        old_columns = self.set_parameters()
        self.normalize(transfers, valid_duplicates)
        analysis = self.analyze()
        self.data = self.data[old_columns.to_list()]
        self.sort_fields()
        return analysis

    def exceptions(self, analysis: dict[AFIField, Index | MultiIndex]):
        """
        Obtiene todos los errores y los mensajes propios por cada campo de la interfaz contable.
        """
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [AFIException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in AFIException and len(idx) > 0]

        fields_warnings = [AFIWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in AFIWarning and len(idx) > 0]

        return (
            NoMatchAFIFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectAFIFieldsWarning(incorrect_fields) if incorrect_fields else None,
            *fields_exceptions,
            *fields_warnings
        )
