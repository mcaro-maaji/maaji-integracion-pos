"""Modulo para definir parametros generales de los servicios."""

from typing import Literal
from uuid import UUID
from io import BytesIO
from os import PathLike, fsdecode
from pathlib import Path
from codecs import lookup as lookup_codec
from pandas import Series
from service.decorator import services
from service.parameters import ServiceOptParameter, P, R
from utils.typing import JsonFrameOrient, ListJsonFrameOrient, REPR_JSONFRAME_ORIENT

@services.parameter(type="string")
def string(value: str):
    """Parametro que recibe un string con informacion."""
    if isinstance(value, str):
        return value
    raise TypeError("el valor debe ser de tipo 'string'")

@services.parameter(type="string")
def raw(value: str):
    """Parametro que recibe un string con informacion y no debe ser vacio."""
    if string(value):
        return value
    raise TypeError("el valor debe ser de tipo 'string' y no vacio.")

@services.parameter(type="boolean")
def boolean(value: bool):
    """parametro que valida que el valor sea de tipo boleano."""
    if isinstance(value, bool):
        return value
    raise TypeError("el valor debe ser de tipo boleano.")

@services.parameter(type="string[UUID]")
def uuid(value: str | UUID):
    """Parametro para validar un string UUID, devuelve una instancia."""
    if isinstance(value, UUID):
        return value
    if isinstance(value, str) and value:
        try:
            return UUID(value)
        except ValueError:
            pass
    raise TypeError("el valor debe ser de un tipo string | UUID.")

@services.parameter(type="end | [start, end, step]")
def index(value: int | tuple[int, int, int]):
    """Parametro que recibe un listado que componen un indice."""
    if isinstance(value, (tuple, list)) and all(isinstance(i, int) for i in value[:3]):
        return slice(*value[:3])
    if isinstance(value, int):
        return slice(value)
    raise TypeError("los valores de los indices deben ser numeros.")

@services.parameter(type="string[PathLike]")
def path(value: str | bytes | PathLike):
    """Parametro que recibe la ruta de un archivo."""
    if not value:
        raise TypeError("el valor debe ser de tipo 'string[PathLike]' y no vacio.")
    value = Path(fsdecode(value))
    if not value.is_file():
        raise FileNotFoundError(f"archivo no encontrado en la ruta: {value}")
    return value

@services.parameter(type="string")
def delimeter(value):
    """Parametro que recibe el delimitador al leer un set de datos."""
    return raw(value)

@services.parameter(type="string")
def sep(value):
    """Parametro que recibe el separador al leer un set de datos."""
    return raw(value)

@services.parameter(type="string")
def encoding(value: str):
    """Parametro que debe recibir un encoding valido."""
    try:
        lookup_codec(raw(value))
        return value
    except LookupError as err:
        raise LookupError(f"encoding no valido: '{value}'") from err

@services.parameter(type="string[Bytes]")
def bufferbytes(value: str, _encoding: str = "uft-8"):
    """Parametro que debe recibir un string, lo convierte a un buffer bytes."""
    value = raw(value)
    _encoding = encoding(_encoding)
    return BytesIO(value.encode(_encoding))

@services.parameter(type=REPR_JSONFRAME_ORIENT)
def orientjson(value: JsonFrameOrient):
    """Parametro que indica la orientacion del json."""
    value = raw(value)
    if value in ListJsonFrameOrient:
        return value
    raise ValueError("se debe elegir el alguno de los valores: " + REPR_JSONFRAME_ORIENT)

@services.parameter(type="'columns'|'rows'")
def axis(value: Literal["columns", "rows"]):
    """Parametro que indica el tipo de axis, si son columnas o filas en un objecto tipo tabla."""
    if value in ["columns", "rows"]:
        return value
    raise ValueError("se debe elegir el alguno de estos axis: 'columns'|'rows'")

@services.parameter(type="ArrayList")
def arraylist(value: list):
    """Parametro que comprueba si el valor de tipo ArrayList"""
    if isinstance(value, (list, tuple)):
        return value
    raise TypeError("el valor debe ser de tipo ArrayList.")

def optional(param: ServiceOptParameter[P, R]) -> ServiceOptParameter[P, R | None]:
    """Convierte un parametro a uno opcional, devolviendo un None."""
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        if not args:
            return None
        return param.func(*args, **kwargs)

    return ServiceOptParameter(wrapper, name=param.name, type=param.type, desc=param.desc)

@services.parameter(type="[string, string]")
def series(value: list[object]):
    """Parametro que convierte el valor en uno tipo pandas.Series"""
    value = arraylist(value)
    return Series(value)
