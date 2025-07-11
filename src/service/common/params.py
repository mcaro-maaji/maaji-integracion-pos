"""Modulo para definir parametros generales de los servicios."""

from typing import Literal
from uuid import UUID
from io import BytesIO
from os import PathLike, fsdecode
from pathlib import Path
from codecs import lookup as lookup_codec
from datetime import datetime as _datetime, timedelta as _timedelta
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

@services.parameter(type="string[]")
def fields(value: list[str]):
    """Parametro que verifica que el valor es de tipo ArrayList con valores tipo string"""
    value = arraylist(value)
    contain_str = all(isinstance(i, str) for i in value)
    if contain_str:
        return value
    raise TypeError("el valor arraylist debe contener valores tipo string.")

@services.parameter(type="DateTime")
def datetime(value: str | _datetime) -> _datetime:
    """Parametro que valida un string a una fecha manipulable, literal 'now' o formato ISO8601."""
    if isinstance(value, _datetime):
        return value
    if value == "now":
        return _datetime.now()
    try:
        return _datetime.fromisoformat(value)
    except ValueError as err:
        raise ValueError("el formato de la fecha debe ser ISO8601.") from err

@services.parameter(type="'infer' | boolean | string[] | number | number[] | None")
def header(value: str | int | bool | list[str | int] | None):
    """
    Parametro que verifica si el encabezado de una tabla, numero para la fila o None si no tiene.
    """
    if value == "infer" or isinstance(value, (int, bool, list, tuple)) or value is None:
        return value
    raise TypeError("debe ser de tipo 'infer' | boolean | string[] | number | number[] | None")

@services.parameter(type="string | None")
def filename(value: str | None):
    """Parametro que recibe un string con el nombre de un archivo o nulo si no hay nombre."""
    if isinstance(value, str) or value is None:
        return value
    raise TypeError("el valor debe ser de tipo 'string' o None")

@services.parameter(type="TimeDelta")
def timedelta(value: str) -> _timedelta:
    """Parametro que convierte un string a un objeto timedelta."""
    if not isinstance(value, (str, _timedelta)):
        raise TypeError("el valor debe ser de tipo string o TimeDelta")
    if isinstance(value, _timedelta):
        return value
    try:
        # Format 1: # weeks, # days, hours:minutes:seconds:microseconds:milliseconds
        # Format 2: # days, hours:minutes:seconds:microseconds:milliseconds
        value_parts = value.strip().split(", ")
        if not value_parts:
            raise ValueError("...")

        if ":" in value_parts[-1]:
            time_parts = value_parts.pop()
        else:
            time_parts = "00:00:00"

        if len(value_parts) == 2 and " weeks" in value_parts[0] and " days" in value_parts[1]:
            [weeks_part, days_part] = value_parts
        elif len(value_parts) == 1 and " days" in value_parts[0]:
            [weeks_part, days_part] = (None, value_parts[0])
        else:
            [weeks_part, days_part] = (None, None)

        num_weeks = 0. if weeks_part is None else float(weeks_part.replace(" weeks", ""))
        num_days = 0. if days_part is None else float(days_part.replace(" days", ""))
        num_times = map(float, time_parts.split(":"))
        keys = ("weeks", "days", "hours", "minutes", "seconds", "microseconds", "milliseconds")
        items = zip(keys, [num_weeks, num_days, *num_times])
        kwargs = {}
        kwargs.update(items)
        delta = _timedelta(**kwargs)

        if not delta:
            raise ValueError("...")
        return delta
    except ValueError as err:
        raise ValueError("el valor debe cumplir con el formato TimeDelta[string]") from err

@services.parameter(type="DateTime")
def datetimefromdelta(value: str | _datetime | _timedelta):
    """Parametro que verifica si es datetime, si es timedelta se suma a la fecha actual."""
    if isinstance(value, str):
        try:
            return datetime(value)
        except ValueError:
            pass
        if value.startswith("now"):
            value = value.removeprefix("now")
        try:
            return _datetime.now() + timedelta(value)
        except ValueError as err:
            raise ValueError("el valor debe ser tipo DateTime[string] | TimeDelta[string]") from err
    if isinstance(value, _timedelta):
        return _datetime.now() + value
    if isinstance(value, _datetime):
        return value

    raise TypeError("el valor debe ser de tipo string | datetime | timedelta")

@services.parameter(type="string")
def username(value: str):
    """Parametro para obtener un nombre de usuario."""
    return string(value)

@services.parameter(type="string")
def password(value: str):
    """Parametro para obtener la contraseña de un usuario."""
    return string(value)
