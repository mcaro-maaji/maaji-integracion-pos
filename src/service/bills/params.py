"""Modulo para definir parametros del servicio de facturas de compra: core.bills"""

from uuid import UUID
from providers.microsoft.api.dynamics import DynamicsKeyEnv
from service import common
from service.decorator import services

@services.parameter(type="Bills[UUID]")
def dataid(value: str | UUID):
    """Parametro para contiene el ID de los datos de los facturas."""
    return common.params.uuid(value)

@services.parameter(type="boolean")
def fixed(value: bool = False):
    """Parametro que escoge si la data de facturas debe ser los reparados, por defecto no."""
    return common.params.boolean(value)

@services.parameter(type="boolean")
def force(value: bool = False):
    """Parametro para forzar la creacion de los datos de los facturas, hace espacio en memoria."""
    return common.params.boolean(value)

@services.parameter(type="boolean")
def excel(value: bool = True):
    """Parametro para leer la informacion de los facturas desde el Clipboard como excel."""
    return common.params.boolean(value)

@services.parameter(type="boolean")
def index(value: bool = False):
    """Parametro para establecer si se guarda la informacion de los facturas con el indice."""
    return common.params.boolean(value)

@services.parameter(type="[[string, [object, ...]], ...]")
def dataupdate(value: list[tuple[str, list[object]]]):
    """Parametro que verifica que sea un mapping con llaves string y un listado de datos."""
    value = common.params.arraylist(value)
    try:
        return {common.params.raw(k): common.params.arraylist(v) for k, v in value}
    except ValueError:
        pass
    raise TypeError("el contenido del valor debe ser de tipo [string, [object, ...]]")

@services.parameter(type="string[] | number[]")
def indices(value: list[str] | list[int]):
    """Parametro que verifica que el valor es tipo ArrayList con valores tipo string o number."""
    value = common.params.arraylist(value)
    contain_str_or_int = all(isinstance(i, (str, int)) for i in value)
    if contain_str_or_int:
        return value
    raise TypeError("el valor indices debe contener valores tipo string o number.")

@services.parameter(type="[[string, [number, ...]], ...]")
def analysis(value: list[tuple[str, list[int]]]):
    """Parametro de informacion sobre facturas, donde las llaves son el campo y los valores
    son los indices de las filas con errores."""
    content = dataupdate(value)
    for i in content.values():
        indices(i)
    return content

@services.parameter(type="DynamicsApi[DataAreaId]")
def areaid(value: str):
    """
    Parametro que valida el id del area de la empresa donde se extraen los datos
    desde la api Dynamics 365.
    """
    return common.params.raw(value)

@services.parameter(type="DynamicsKeyEnv['PROD'|'UAT']")
def dynamicsenv(value: str) -> DynamicsKeyEnv:
    """Parametro que verifica que el entorno de la api de Dynamics sea el correcto."""
    if value in ["PROD", "UAT"]:
        return value
    raise TypeError("el valor debe ser 'PROD'|'UAT'")
