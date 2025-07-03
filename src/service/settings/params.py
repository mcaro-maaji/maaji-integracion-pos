"""Modulo para definir parametros del servicio de las configuraciones: core.settings"""

from typing import Literal
from service import common
from service.decorator import services

@services.parameter(type="boolean")
def excel(value: bool = True):
    """Parametro para leer la informacion de las configuraciones desde el Clipboard como excel."""
    return common.params.boolean(value)

@services.parameter(type="boolean")
def index(value: bool = False):
    """
    Parametro para establecer si se guarda la informacion de las configuraciones con el indice.
    """
    return common.params.boolean(value)

SettingsKeyName = Literal["municipios", "stores", "providers", "afiparameters"]
settings_keyname: list[SettingsKeyName] = ["municipios", "stores", "providers", "afiparameters"]
repr_settings_keyname = "|".join(settings_keyname)

@services.parameter(type=repr_settings_keyname)
def keyname(value: SettingsKeyName):
    """Parametro que el nombre clave de alguna configuracion."""
    if value in settings_keyname:
        return value
    raise ValueError("se debe elegir el alguno de estos keynames: " + repr_settings_keyname)
