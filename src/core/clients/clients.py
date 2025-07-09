"""Modulo para la lectura, analisis y correccion de clientes."""

from datetime import datetime
from pandas import (
    DataFrame,
    Index,
    MultiIndex,
    Series,
    concat as pandas_concat
)
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from core.dane import DANE_MUNICIPIOS, DaneMunicipiosField
from .fields import ClientField
from .exceptions import (
    ClientsException,
    ClientsWarning,
    NoMatchClientFieldsWarning,
    IncorrectClientFieldsWarning,
    MaxClientsWarning,
    WARNING_MAX_CLIENTS
)

class Clients(BaseDataIO):
    """Clase para la gestion de datos de los clientes."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la inforamcion de los clientes."""

        super().__init__(source, destination, support, mode)
        self.load(dtype=str, **kwargs)          # Lectura de datos siempre en String
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in ClientField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(ClientField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[ClientField] = None):
        """Organiza los campos de los clientes y elimina los incorrectos."""
        if not fields:
            fields = list(ClientField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[ClientField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def normalize(self):
        """
        Aplica en los datos los siguientes puntos:
            - Agrega los campos que no existen.
            - Los valores que van en Mayusculas.
            - Quita los espacios en blanco antes y despues de cada dato.
            - Corrige fechas al formato '%d/%m/%Y'.
            - Elimina los registros del numero del cliente '222222222'
        """
        fields_exclude_mayus = {
            ClientField.FORMULADIRECCION,
            ClientField.FORMULADIRECCIONMM,
            ClientField.CORREOSELECTRONICOS,
            ClientField.CORREOCONTACTO
        }

        fields_dates = {
            ClientField.FECHADENACIMIENTO,
            ClientField.FECHADECREACION
        }

        # Añadir columnas faltantes con valores vacios usando pandas.concat
        missing_fields = {
            field: Series("", index=self.data.index, dtype=str)
            for field in ClientField
            if field not in self.data
        }
        if missing_fields:
            self.data = pandas_concat([self.data, DataFrame(missing_fields)], axis=1)

        # Procesar campos en grupos:
        #  - todo en mayusculas, excepto algunos campos.
        #  - elimina los espacios en blancos.
        #  - da formato a fechas.

        def format_date(value: str):
            try:
                datetime.strptime(value, "%d/%m/%Y")
                return value
            except ValueError:
                pass
            try:
                return datetime.fromisoformat(value).strftime("%d/%m/%Y")
            except ValueError:
                pass
            return value

        updates: dict[ClientField, Series] = {}
        for field in ClientField:
            if field not in self.data:
                continue
            series = self.data[field]

            if field not in fields_exclude_mayus:
                series = series.str.upper()

            updates[field] = series.str.strip()

            if field in fields_dates and field in updates:
                updates[field] = updates[field].astype(str).apply(format_date)

        # Todos los cambios en una sola aplicacion al dataframe.
        self.data.update(updates)

        # Filtrar los clientes excluidos, ej 222222222

        excluded_numero_documento = ["222222222"]
        numero_documento = self.data[ClientField.NUMERODOCUMENTO]
        numero_documento = numero_documento.isin(excluded_numero_documento)
        numero_documento = numero_documento[numero_documento]
        self.data.drop(index=numero_documento.index, inplace=True)

    def analyze(self):
        """Analiza los datos y devuelve los erroes encontrados."""

        def idx(field: ClientField, value: str):
            """Verifica si el campo tiene un valor por defecto o si es vacio regresa los indices."""
            df_field = self.data[field]
            if value:
                return df_field[df_field != value].index # filas con valor por defecto
            return df_field[df_field == value].index # filas vacias

        df_field = self.data[ClientField.TIPOIDENTIFICACION]
        list_tipos_identificacion = ["CC", "PA", "CE", "IE", "NI", "SI", "TE", "TI", "TEL"]
        tipos_identificacion = df_field.isin(list_tipos_identificacion)
        tipos_identificacion = tipos_identificacion[~tipos_identificacion].index

        df_codigo_postal = self.data[ClientField.CODIGOPOSTAL].astype(str)
        codigo_postal = df_codigo_postal.isin(DANE_MUNICIPIOS.data[DaneMunicipiosField.CODIGO_POSTAL])
        codigo_postal = codigo_postal[~codigo_postal].index

        df_field = self.data[ClientField.SEXO]
        cliente_sexo = df_field.isin(["F", "M"])
        cliente_sexo = cliente_sexo[~cliente_sexo | (df_field == "")].index

        df_field = self.data[ClientField.PROVEEDOR]
        proveedor = df_field[~(df_field == "")].index

        df_field = self.data[ClientField.CLIENTE]
        cliente = df_field.isin(["X"])
        cliente = cliente[~cliente].index

        df_field = self.data[ClientField.DEPARTAMENTO].astype(str)
        departamento = df_field.eq(df_codigo_postal.apply(lambda x: x[:2]))
        departamento = departamento[~departamento].index

        def valid_date(value: str):
            if value == "00/00/1900":
                return True
            try:
                datetime.strptime(value, "%d/%m/%Y")
                return True
            except ValueError:
                pass
            try:
                datetime.fromisoformat(value)
                return True
            except ValueError:
                return False

        df_field = self.data[ClientField.FECHADECREACION].astype(str)
        fecha_creacion = df_field.apply(valid_date)
        fecha_creacion = df_field[~fecha_creacion].index

        df_field = self.data[ClientField.FECHADENACIMIENTO].astype(str)
        fecha_nacimiento = df_field.apply(valid_date)
        fecha_nacimiento = df_field[~fecha_nacimiento].index

        facturacion_elec_contacto = idx(ClientField.FACTURACIONELECTRONICACONTACTO, "X")

        return {
            ClientField.TIPOIDENTIFICACION: tipos_identificacion,
            ClientField.NUMERODOCUMENTO: idx(ClientField.NUMERODOCUMENTO, ""),
            ClientField.CODIGOPOSTAL: codigo_postal,
            ClientField.NOMBRERAZONSOCIAL: idx(ClientField.NOMBRERAZONSOCIAL, ""),
            ClientField.NOMBRE2: idx(ClientField.NOMBRE2, ""),
            ClientField.APELLIDO1: idx(ClientField.APELLIDO1, ""),
            ClientField.APELLIDO2: idx(ClientField.APELLIDO2, ""),
            ClientField.SEXO: cliente_sexo,
            ClientField.PROVEEDOR: proveedor,
            ClientField.CLIENTE: cliente,
            ClientField.FORMULADIRECCION: idx(ClientField.FORMULADIRECCION, ""),
            ClientField.FORMULADIRECCIONMM: idx(ClientField.FORMULADIRECCIONMM, ""),
            ClientField.TELEFONO1: idx(ClientField.TELEFONO1, ""),
            ClientField.TELEFONOMOVIL: idx(ClientField.TELEFONOMOVIL, ""),
            ClientField.CORREOCONTACTO: idx(ClientField.CORREOCONTACTO, ""),
            ClientField.FECHADENACIMIENTO: fecha_nacimiento,
            ClientField.FECHADECREACION: fecha_creacion,
            ClientField.ESTADO: idx(ClientField.ESTADO, "ACTIVO"),
            ClientField.REGIMENVENTAS: idx(ClientField.REGIMENVENTAS, "SIMPLIFICADO"),
            ClientField.CODIGONATURALEZAJURIDICA: idx(ClientField.CODIGONATURALEZAJURIDICA, "2"),
            ClientField.CODIGOACTIVIDADECONOMICA: idx(ClientField.CODIGOACTIVIDADECONOMICA, "0010"),
            ClientField.CODIGOCLASIFICACIONRENTA: idx(ClientField.CODIGOCLASIFICACIONRENTA, "PND"),
            ClientField.NOMBRECONTACTO: idx(ClientField.NOMBRECONTACTO, ""),
            ClientField.CARGOCONTACTO: idx(ClientField.CARGOCONTACTO, "CLIENTE"),
            ClientField.FACTURACIONELECTRONICACONTACTO: facturacion_elec_contacto,
            ClientField.PAIS: idx(ClientField.PAIS, "169"),
            ClientField.DEPARTAMENTO: departamento,
            ClientField.DIVISA: idx(ClientField.DIVISA, "COP")
        }

    def autofix_default(self,
                        analysis: dict[ClientField, Index | MultiIndex],
                        all_updates: dict[ClientField, Series]):
        """Corrige los campos que tienen un valor por defecto."""
        default_values = {
            ClientField.CLIENTE: "X",
            ClientField.PROVEEDOR: "",
            ClientField.FECHADENACIMIENTO: "00/00/1900",
            ClientField.FECHADECREACION: "00/00/1900",
            ClientField.ESTADO: "ACTIVO",
            ClientField.REGIMENVENTAS: "SIMPLIFICADO",
            ClientField.CODIGONATURALEZAJURIDICA: "2",
            ClientField.CODIGOACTIVIDADECONOMICA: "0010",
            ClientField.CODIGOCLASIFICACIONRENTA: "PND",
            ClientField.CARGOCONTACTO: "CLIENTE",
            ClientField.FACTURACIONELECTRONICACONTACTO: "X",
            ClientField.PAIS: "169",
            ClientField.DIVISA: "COP"
        }

        for field, value in default_values.items():
            if field in analysis and len(analysis[field]) > 0:
                all_updates[field] = Series(value, index=analysis[field])

    def autofix_numero_doc_cliente(self,
                                   analysis: dict[ClientField, Index | MultiIndex],
                                   all_updates: dict[ClientField, Series]):
        """Añadir actualizaciones respecto al numero de documento del cliente."""
        if len(analysis[ClientField.NUMERODOCUMENTO]) == 0:
            def first_chr(value: str):
                if not value:
                    return ""
                return value[0]

            fchr_num_documento = self.data[ClientField.NUMERODOCUMENTO].astype(str).apply(first_chr)

            all_updates.update({
                ClientField.CODIGOALTERNO1: self.data[ClientField.NUMERODOCUMENTO],
                ClientField.NUMERODOCUMENTOCONTACTO: self.data[ClientField.NUMERODOCUMENTO],
                ClientField.CODIGOALTERNOCONTACTO: fchr_num_documento
            })

    def autofix_codigo_postal(self,
                              _: dict[ClientField, Index | MultiIndex],
                              all_updates: dict[ClientField, Series]):
        """Añadir actualizaciones respecto al codigo postal de los clientes."""
        codigo_postal = self.data[ClientField.CODIGOPOSTAL].str[:5]
        departamento = codigo_postal.str[:2]

        all_updates.update({
            ClientField.CODIGOPOSTAL: codigo_postal,
            ClientField.CODIGOCIUDAD: codigo_postal,
            ClientField.DEPARTAMENTO: departamento
        })

    def autofix_nombre_completo(self,
                                analysis: dict[ClientField, Index | MultiIndex],
                                all_updates: dict[ClientField, Series]):
        """Corrige los campos respecto a los nombres de los clientes y de tipo empresas."""
        nombre_completo = (
            self.data[ClientField.NOMBRERAZONSOCIAL] + " " +
            self.data[ClientField.NOMBRE2] + " " +
            self.data[ClientField.APELLIDO1] + " " +
            self.data[ClientField.APELLIDO2]
        ).str.strip()

        idx_nombre_contacto = analysis[ClientField.NOMBRECONTACTO]
        if len(idx_nombre_contacto) > 0:
            all_updates[ClientField.NOMBRECONTACTO] = nombre_completo.loc[idx_nombre_contacto]

        # Nombres completos de las empresas
        if len(analysis[ClientField.TIPOIDENTIFICACION]) == 0:
            idx_empresas = self.data[self.data[ClientField.TIPOIDENTIFICACION] == "NI"].index
            if len(idx_empresas) > 0:
                nombre_contacto = self.data.loc[idx_empresas, ClientField.NOMBRECONTACTO]
                all_updates[ClientField.RAZONSOCIALNOMBRES] = nombre_contacto

    def autofix_direccion(self,
                          analysis: dict[ClientField, Index | MultiIndex],
                          all_updates: dict[ClientField, Series]):
        """Corrige los campos respecto a las direcciones de los clientes."""
        idx_direccion = analysis[ClientField.FORMULADIRECCIONMM]
        if len(idx_direccion) > 0:
            map_municipios = DANE_MUNICIPIOS.data.set_index(DaneMunicipiosField.CODIGO_POSTAL)
            map_municipios = map_municipios[DaneMunicipiosField.MUNICIPIO].to_dict()
            municipios = self.data.loc[idx_direccion, ClientField.CODIGOPOSTAL].map(
                lambda x: map_municipios.get(x, "CALLE")
            )
            all_updates[ClientField.FORMULADIRECCIONMM] = municipios
            all_updates[ClientField.FORMULADIRECCION] = municipios

    def autofix(self, analysis: dict[ClientField, Index | MultiIndex]):
        """Modifica los datos de los clientes, corrige los valores y establece por defecto."""
        # Recoleta todas las actualizaciones en un solo diccionario.
        all_updates = {}

        # Actualizaciones respecto a los valores por defecto.
        self.autofix_default(analysis, all_updates)
        # Actualizaciones respecto a numero documento de los clientes.
        self.autofix_numero_doc_cliente(analysis, all_updates)
        # Actualizaciones respecto a los codigos postales en la direccion de los clientes.
        self.autofix_codigo_postal(analysis, all_updates)
        # Actualizaciones respecto al nombre de los clientes.
        self.autofix_nombre_completo(analysis, all_updates)
        # Actualizaciones respecto a la direcciones de los clientes.
        self.autofix_direccion(analysis, all_updates)

        # Aplicar todas las actualizaciones recopiladas a la vez si existe alguna.
        if all_updates:
            self.data.update(all_updates)

    def fullfix(self):
        """Ejecuta la auto reparacion de los datos de los clientes."""
        self.normalize()
        analysis = self.analyze()
        self.autofix(analysis)
        self.sort_fields()
        return self.analyze()

    def exceptions(self, analysis: dict[ClientField, Index | MultiIndex]):
        """Obtiene todos los errores y los mensajes propios por cada campo de los clientes."""
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [ClientsException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in ClientsException and len(idx) > 0]

        fields_warnings = [ClientsWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in ClientsWarning and len(idx) > 0]

        return (
            NoMatchClientFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectClientFieldsWarning(incorrect_fields) if incorrect_fields else None,
            MaxClientsWarning() if self.data.index.size >= WARNING_MAX_CLIENTS else None,
            *fields_exceptions,
            *fields_warnings
        )
