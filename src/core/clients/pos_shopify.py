"""Modulo para organizar la inforamcion de los clientes segun el Sistema POS de CEGID Y2 Retail."""

from typing import LiteralString
from io import StringIO
from datetime import datetime
from pandas import DataFrame
from utils.json import from_json
from utils.dataclass import dict_to_dtcls
from utils.typing import FilePath, ReadBuffer
from utils.mapfields import MapFields, MapFieldsFunc
from .pos import ClientsPOS
from .fields import (
    ClientField as CF, ClientFieldShopifyMx as CFSM,
    ClientShopifyJson as CSJ, ClientShopifyJsonAddress as CSJA,
    ClientShopifyJsonMetaField as CSJM
)

class ClientsShopify(ClientsPOS[CFSM]):
    """Clientes que se manejan en SHOPIFY POS."""

    __date_format: str = "%Y-%m-%d %H:%M:%S %z"
    __fields_apostrophe: set[CFSM] = {CFSM.PHONE, CFSM.ADDRESS_PHONE}

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
        fields_date = {CFSM.CREATED_AT}

        def format_date(value: str):
            try:
                return datetime.strptime(value, self.date_format).isoformat()
            except ValueError:
                return value

        for field_date in fields_date:
            if field_date in self.data_pos:
                self.data_pos[field_date] = self.data_pos[field_date].apply(format_date)

        # Nombres
        in_field_second_name = CFSM.SECOND_NAME in self.data_pos
        in_field_second_lname = CFSM.SECOND_LAST_NAME in self.data_pos
        if CFSM.FIRST_NAME in self.data_pos and not in_field_second_name:
            df_name = self.data_pos[CFSM.FIRST_NAME].str.split(n=1, expand=True).fillna("")
            if not 1 in df_name:
                df_name[1] = ""
            self.data_pos[[CFSM.FIRST_NAME, CFSM.SECOND_NAME]] = df_name
        if CFSM.LAST_NAME in self.data_pos and not in_field_second_lname:
            df_lname = self.data_pos[CFSM.LAST_NAME].str.split(n=1, expand=True).fillna("")
            if not 1 in df_lname:
                df_lname[1] = ""
            self.data_pos[[CFSM.LAST_NAME, CFSM.SECOND_LAST_NAME]] = df_lname

        # Telefonos
        fields_phone = {CFSM.PHONE, CFSM.ADDRESS_PHONE}
        for field in fields_phone:
            if field in self.data_pos:
                self.data_pos[field] = self.data_pos[field].str.removeprefix("+57")

        # Union Direcciones
        in_field_addres_2 = CFSM.ADDRESS_LINE_2 in self.data_pos
        if CFSM.ADDRESS_LINE_1 in self.data_pos and in_field_addres_2:
            def join_address(row):
                if row[CFSM.ADDRESS_LINE_2].strip() == '':
                    return row[CFSM.ADDRESS_LINE_1]
                return row[CFSM.ADDRESS_LINE_1] + ', ' + row[CFSM.ADDRESS_LINE_2]

            self.data_pos[CFSM.ADDRESS_LINE_1] = self.data_pos.apply(join_address, axis=1)
            self.data_pos = self.data_pos.drop(CFSM.ADDRESS_LINE_2, axis=1)

        # Eliminar clientes repetidos donde la direccion no sea la predeterminada.
        if CFSM.ADDRESS_IS_DEFAULT in self.data_pos:
            values = self.data_pos[CFSM.ADDRESS_IS_DEFAULT].str.upper().isin(['TRUE', 'VERDADERO'])
            del_index = self.data_pos[~values].index
            self.data_pos = self.data_pos.drop(del_index)
            self.data = self.data.drop(del_index)

        super().normalize()

    @classmethod
    def from_dataclasses(cls, dataclasses: list[CSJ], *, mapfields: MapFields[CFSM, CF]):
        """Pasa la informacion de los clientes de un listado de dataclasses a uno ClientShopify.
        API de Shopify Version: 2024-01
        """
        df_clients = cls(StringIO("|".join(CFSM)), mapfields=mapfields)
        data = []

        for dtcls in dataclasses:
            dtcls_metafield_tipo_de_documento = ""

            for metafield in dtcls.metafields:
                is_custom = metafield.namespace == "custom"
                is_tipo_documento = metafield.key == "tipo_de_documento"
                is_single_line_text = metafield.type == "single_line_text_field"
                if is_custom and is_tipo_documento and is_single_line_text:
                    dtcls_metafield_tipo_de_documento = metafield.value
                    break

            dt_dict = {
                CFSM.ID: str(dtcls.id or ""),
                CFSM.EMAIL: dtcls.email,
                CFSM.FIRST_NAME: dtcls.first_name,
                CFSM.LAST_NAME: dtcls.last_name,
                CFSM.PHONE: dtcls.default_address.phone,
                CFSM.CREATED_AT: dtcls.created_at,
                CFSM.ADDRESS_ID: str(dtcls.default_address.id or ""),
                CFSM.ADDRESS_PHONE: dtcls.default_address.phone,
                CFSM.ADDRESS_COMPANY: dtcls.default_address.company,
                CFSM.ADDRESS_LINE_1: dtcls.default_address.address1,
                CFSM.ADDRESS_LINE_2: dtcls.default_address.address2,
                CFSM.ADDRESS_CITY: dtcls.default_address.city,
                CFSM.ADDRESS_PROVINCE: dtcls.default_address.province,
                CFSM.ADDRESS_COUNTRY: dtcls.default_address.country,
                CFSM.ADDRESS_ZIP: dtcls.default_address.zip,
                CFSM.ADDRESS_IS_DEFAULT: "VERDADERO" if dtcls.default_address.default else "",
                CFSM.MF_TIPO_DE_DOCUMENTO: dtcls_metafield_tipo_de_documento,
            }
            data.append(dt_dict)

        df_clients.data_pos = DataFrame(data).fillna("")
        df_clients.data = df_clients.data_pos.copy()
        df_clients.fields_apostrophe = set()
        return df_clients

    @classmethod
    def from_json(cls, source: FilePath | LiteralString | ReadBuffer | dict, *,
                  mapfields: MapFields[CFSM, CF]):
        """Obtener los clientes de Shopify mediante el formato JSON,
        API de Shopify Version: 2024-01"""
        data = from_json(source)

        if not isinstance(data, dict) or "customers" not in data or "metafields" not in data:
            json_format = '{"customers": [{...}, ...], "metafields": [{...}, ...]}'
            raise TypeError(f"El JSON debe tener este formato: '{json_format}'")

        customers = data["customers"]
        address = "default_address"
        customers = [dict_to_dtcls(CSJ, {**c, address: CSJA(**c[address])}) for c in customers]
        metafields: dict[int, list[CSJM]] = {}

        for mfield in data["metafields"]:
            mfield = dict_to_dtcls(CSJM, mfield)
            if mfield.owner_id not in metafields:
                metafields[mfield.owner_id] = []
            metafields[mfield.owner_id].append(mfield)

        for customer in customers:
            customer.metafields = metafields[customer.id]

        return cls.from_dataclasses(customers, mapfields=mapfields)

MAPFIELDS_POS_SHOPIFY_MX = MapFields(
    (CFSM.ADDRESS_COMPANY, CF.NUMERODOCUMENTO),
    (CFSM.ADDRESS_ZIP, CF.CODIGOPOSTAL),
    (CFSM.FIRST_NAME, CF.NOMBRERAZONSOCIAL),
    (CFSM.SECOND_NAME, CF.NOMBRE2),
    (CFSM.LAST_NAME, CF.APELLIDO1),
    (CFSM.SECOND_LAST_NAME, CF.APELLIDO2),
    (CFSM.ADDRESS_LINE_1, CF.FORMULADIRECCION),
    (CFSM.ADDRESS_LINE_1, CF.FORMULADIRECCIONMM),
    (CFSM.ADDRESS_PHONE, CF.TELEFONO1),
    (CFSM.PHONE, CF.TELEFONOMOVIL),
    (CFSM.EMAIL, CF.CORREOCONTACTO),
    (CFSM.CREATED_AT, CF.FECHADECREACION),
    (CFSM.ADDRESS_PROVINCE, CF.DEPARTAMENTO),
    mapdata={
        (CFSM.MF_TIPO_DE_DOCUMENTO, CF.TIPOIDENTIFICACION): [
            (MapFieldsFunc.EQ, {
                "Cédula de ciudadanía": "CC",
                "Cédula de extranjería": "CE",
                "Pasaporte": "PA",
                "NIT": "NI",
                "Tarjeta de extranjería": "TE",
                "Tarjeta de identidad": "TI"
            }),
        ],
        (CFSM.ADDRESS_COUNTRY, CF.PAIS): [(MapFieldsFunc.EQ, {"Colombia": "169"})]
    }
)
