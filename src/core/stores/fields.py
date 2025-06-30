"""Modulo para la definicion de los campos de las tiendas Maaji."""

from enum import StrEnum

class StoreField(StrEnum):
    """Campos de las columnas sobre las tiendas con informacion basica."""
    CODIGO_TIENDA = "Codigo Tienda"
    NOMBRE_TIENDA = "Nombre Tienda"
    OTROS_NOMBRES = "Otros Nombres"
    CODIGO_POSTAL = "Codigo Postal"
    CODIGO_ALMACEN = "Codigo Almacen"
    NOMBRE_ALMACEN = "Nombre Almacen"
