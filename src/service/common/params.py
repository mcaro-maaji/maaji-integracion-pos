"""Modulo para definir parametros generales de los servicios."""

from typing import TypeAlias, Literal
from uuid import UUID
from io import BytesIO
from pathlib import Path
from codecs import lookup as lookup_codec
from service.decorator import services

@services.parameter(type="string")
def raw(value: str):
    """Parametro que recibe un string con informacion y no debe ser vacio."""
    if isinstance(value, str) and value:
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

@services.parameter(type="string[Path]")
def fpath(value: str | Path):
    """Parametro que recibe la ruta de un archivo."""
    if not value:
        raise TypeError("el valor debe ser de tipo 'string | Path' y no vacio.")
    path = Path(value)
    if not path.is_file():
        raise FileNotFoundError(f"archivo no encontrado en la ruta: {value}")
    return path

@services.parameter(type="'csv'|'excel'|'json'")
def ftype(value: str):
    """Parametro para validar el mimetype permitidos por los servicios."""
    if value in ["csv", "excel", "json"]:
        return value
    raise ValueError("se debe elegir el alguno de estos ftype: 'csv'|'excel'|'json'")

@services.parameter(type="string")
def delimeter(value):
    """Parametro que recibe el delimitador al leer un archivo."""
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

JsonFrameOrient: TypeAlias = Literal[
    "split", "records", "index", "columns", "values", "table"
]

@services.parameter(type="'split'|'records'|'index'|'columns'|'values'|'table'")
def orientjson(value: JsonFrameOrient):
    """Parametro que indica la orientacion del json."""
    value = raw(value)
    if value in ["split", "records", "index", "columns", "values", "table"]:
        return value
    raise ValueError("el valor debe ser de tipo JsonFrameOrient.")

@services.parameter(type="'columns'|'rows'")
def axis(value: Literal["columns", "rows"]):
    """Parametro que indica el tipo de axis, si son columnas o filas en un objecto tipo tabla."""
    if value in ["columns", "rows"]:
        return value
    raise ValueError("el valor debe ser de tipo string ['columns'|'rows']")

@services.parameter(type="ArrayList")
def arraylist(value: list):
    """Parametro que comprueba si el valor de tipo ArrayList"""
    if isinstance(value, (list, tuple)):
        return value
    raise TypeError("el valor debe ser de tipo ArrayList.")
