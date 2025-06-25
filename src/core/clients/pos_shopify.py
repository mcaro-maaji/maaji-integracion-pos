"""Modulo para organizar la inforamcion de los clientes segun el Sistema POS de CEGID Y2 Retail."""

from datetime import datetime
from core.mapfields import MapFields
from .fields import ClientField, ClientFieldShopify
from .pos import ClientsPOS

class ClientsShopify(ClientsPOS[ClientFieldShopify]):
    """Clientes que se manejan en SHOPIFY POS."""

    __date_format: str = "%Y-%m-%d %H:%M:%S %z"
    __fields_apostrophe = {ClientFieldShopify.PHONE, ClientFieldShopify.ADDRESS_PHONE}

    @property
    def date_format(self):
        """Propiedad para definir el formato de las fechas en los datos de Shopify."""
        return self.__date_format

    @date_format.setter
    def date_format(self, value):
        if not isinstance(value, str):
            raise TypeError(f"El tipo de dato no es valido: {type(value)}")
        self.__date_format = value

    @property
    def fields_apostrophe(self):
        """Propiedad para definir los campos al cual retirarle el apostrofe."""
        return self.__fields_apostrophe

    @fields_apostrophe.setter
    def fields_apostrophe(self, value):
        if not isinstance(value, set):
            raise TypeError(f"El tipo de dato no es valido: {type(value)}")
        self.__fields_apostrophe = value

    def normalize(self):
        """Aplica los siguientes puntos a los datos de Shopify POS:
            - Retira los apostrofes de campos especificos en el df: [PHONE, ADDRESS_PHONE]
            - Verifica las fechas, formato por defecto: "%Y-%m-%d %H:%M:%S %z"
            - Los nombres y apellidos, se separan por nombre 1 y nombre 2, apellido 1 apellido 2.
            - El numero de telefono, retirar el prefijo +57 perteneciente a Colombia.
            - Unir los campos de direccion 'Addres Line 1' y 'Addres Line 2' en uno solo.
            - Eliminar clientes donde el campo 'Addres Is Default' sea diferente de 'VERDADERO'.
        """
        # Apostrofes
        for field in self.fields_apostrophe:
            if field in self.data_pos:
                self.data_pos[field] = self.data_pos[field].str.removeprefix("'")

        # Formato de fechas
        fields_date = {ClientFieldShopify.CREATED_AT}

        def format_date(value: str):
            try:
                return datetime.strptime(value, self.date_format).isoformat()
            except ValueError:
                return value

        for field_date in fields_date:
            if field_date in self.data_pos:
                self.data_pos[field_date] = self.data_pos[field_date].apply(format_date)

        # Nombres
        in_field_second_name = ClientFieldShopify.SECOND_NAME in self.data_pos
        in_field_second_lname = ClientFieldShopify.SECOND_LAST_NAME in self.data_pos

        if ClientFieldShopify.FIRST_NAME in self.data_pos and not in_field_second_name:
            df_name = self.data_pos[ClientFieldShopify.FIRST_NAME]
            df_name = df_name.str.split(n=1, expand=True).fillna("")

            if not 1 in df_name:
                df_name[1] = ""

            mf_name = [ClientFieldShopify.FIRST_NAME, ClientFieldShopify.SECOND_NAME]
            self.data_pos[mf_name] = df_name

        if ClientFieldShopify.LAST_NAME in self.data_pos and not in_field_second_lname:
            df_lname = self.data_pos[ClientFieldShopify.LAST_NAME]
            df_lname = df_lname.str.split(n=1, expand=True).fillna("")

            if not 1 in df_lname:
                df_lname[1] = ""

            mf_lname = [ClientFieldShopify.LAST_NAME, ClientFieldShopify.SECOND_LAST_NAME]
            self.data_pos[mf_lname] = df_lname

        # Telefonos
        fields_phone = {ClientFieldShopify.PHONE, ClientFieldShopify.ADDRESS_PHONE}
        for field in fields_phone:
            if field in self.data_pos:
                self.data_pos[field] = self.data_pos[field].str.removeprefix("+57")

        # Union Direcciones
        in_field_address_2 = ClientFieldShopify.ADDRESS_LINE_2 in self.data_pos
        if ClientFieldShopify.ADDRESS_LINE_1 in self.data_pos and in_field_address_2:
            def join_address(row):
                if row[ClientFieldShopify.ADDRESS_LINE_2].strip() == '':
                    return row[ClientFieldShopify.ADDRESS_LINE_1]

                address = row[ClientFieldShopify.ADDRESS_LINE_1]
                address += ", " + row[ClientFieldShopify.ADDRESS_LINE_2]
                return address

            df_address = self.data_pos.apply(join_address, axis=1)
            self.data_pos[ClientFieldShopify.ADDRESS_LINE_1] = df_address
            self.data_pos = self.data_pos.drop(ClientFieldShopify.ADDRESS_LINE_2, axis=1)

        # Eliminar clientes repetidos donde la direccion no sea la predeterminada.
        if ClientFieldShopify.ADDRESS_IS_DEFAULT in self.data_pos:
            df_address_default = self.data_pos[ClientFieldShopify.ADDRESS_IS_DEFAULT]
            is_address_default = df_address_default.str.upper().isin(['TRUE', 'VERDADERO'])
            del_index = self.data_pos[~is_address_default].index
            self.data_pos = self.data_pos.drop(del_index)
            self.data = self.data.drop(del_index)

        super().normalize()

MAPFIELDS_CLIENTS_POS_SHOPIFY = MapFields(
    (ClientFieldShopify.MF_TIPO_DE_DOCUMENTO, ClientField.TIPOIDENTIFICACION),
    (ClientFieldShopify.ADDRESS_COMPANY, ClientField.NUMERODOCUMENTO),
    (ClientFieldShopify.ADDRESS_ZIP, ClientField.CODIGOPOSTAL),
    (ClientFieldShopify.FIRST_NAME, ClientField.NOMBRERAZONSOCIAL),
    (ClientFieldShopify.SECOND_NAME, ClientField.NOMBRE2),
    (ClientFieldShopify.LAST_NAME, ClientField.APELLIDO1),
    (ClientFieldShopify.SECOND_LAST_NAME, ClientField.APELLIDO2),
    (ClientFieldShopify.ADDRESS_LINE_1, ClientField.FORMULADIRECCIONMM),
    (ClientFieldShopify.ADDRESS_LINE_1, ClientField.FORMULADIRECCION),
    (ClientFieldShopify.ADDRESS_PHONE, ClientField.TELEFONO1),
    (ClientFieldShopify.PHONE, ClientField.TELEFONOMOVIL),
    (ClientFieldShopify.EMAIL, ClientField.CORREOCONTACTO),
    (ClientFieldShopify.CREATED_AT, ClientField.FECHADECREACION),
    (ClientFieldShopify.ADDRESS_COUNTRY, ClientField.PAIS),
    (ClientFieldShopify.ADDRESS_PROVINCE, ClientField.DEPARTAMENTO)
)

_MF_TIPO_DE_DOCUMENTO = ClientFieldShopify.MF_TIPO_DE_DOCUMENTO, ClientField.TIPOIDENTIFICACION
_MF_COUNTRY = ClientFieldShopify.ADDRESS_COUNTRY, ClientField.PAIS

MAPFIELDS_CLIENTS_POS_SHOPIFY[_MF_TIPO_DE_DOCUMENTO].eq.update({
    "Cédula de ciudadanía": "CC",
    "Cédula de extranjería": "CE",
    "Pasaporte": "PA",
    "NIT": "NI",
    "Tarjeta de extranjería": "TE",
    "Tarjeta de identidad": "TI"
})

MAPFIELDS_CLIENTS_POS_SHOPIFY[_MF_COUNTRY].eq["Colombia"] = "169"
