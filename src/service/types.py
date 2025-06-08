"""Modulo para estructurar servicios."""

from typing import (
    TypedDict,
    Any,
    NotRequired,
    TypeGuard,
    Callable,
    Optional,
    Generic,
    TypeVar,
    ParamSpec,
    Union,
    Never,
    overload
)

T = TypeVar("T", bound="ServiceObj")
P = ParamSpec("P")
R = TypeVar("R")

class ServiceParams(TypedDict):
    """Estructura para mapear los parametros de los servicios."""
    parameters: tuple[Any, ...] | list[Any]
    parameterskv: NotRequired[dict[str, Any]]

def is_service_params(value) -> TypeGuard[ServiceParams]:
    """Comprueba que el valor sea de tipo ServiceParams."""
    if not isinstance(value, dict):
        return False
    has_params = "parameters" in value and isinstance(value["parameters"], (list, tuple))
    has_params_kv = "parameterskv" in value and isinstance(value["parameterskv"], dict)
    has_params_kv = has_params_kv and all(isinstance(k, str) for k in value["parameterskv"])
    has_params_kv = has_params_kv or "parameterskv" not in value
    return has_params and has_params_kv

class ServiceResult(Generic[R], TypedDict):
    """Estructura para devolver los datos al consultar el servicio."""
    data: R
    type: str
    errs: NotRequired[str]

def is_service_result(value) -> TypeGuard[ServiceResult]:
    """Comprueba que el valor sea de tipo ServiceResult."""
    if not isinstance(value, dict):
        return False
    has_data = "data" in value
    has_type = "type" in value and isinstance(value["type"], str)
    has_errs = "errs" in value and isinstance(value["errs"], str) or "errs" not in value
    return has_data and has_type and has_errs


class ServiceError(Exception):
    """Errores generales de los servicios."""

class ServiceParamError(ServiceError):
    """Error para identificar errores en los parametros de la operacion del servicio."""

class ServiceNotFound(ServiceError):
    """Error para identificar que no se ha encontrado el servicio."""

class ServiceNotImplementedError(ServiceError):
    """Error para identificar un servicio sin una funcion implementada."""


class ServiceObj(Generic[T, P, R], dict[str, T | list[T]]):
    """Propiedades de estructura basicas para definir, agrupar, clasificar servicios."""
    __name: str
    __type: str
    __func: Optional[Callable[P, R]]
    __desc: str

    def __init__(self, *,
                 name: str,
                 type: str = "",
                 func: Callable[P, R] = None,
                 desc: str = "",
                 **kwargs: T | list[T]):
        super().__init__(**kwargs)
        self.__name = name
        self.__type = type
        self.__func = func
        self.__desc = desc

    @property
    def name(self):
        """Nombre del objeto del servicio."""
        return self.__name
    @property
    def type(self):
        """Tipo de dato de objeto del servicio."""
        return self.__type
    @property
    def func(self):
        """Funcion objeto del servicio util para guardar una funcion que hace parte del servicio."""
        return self.__func
    @property
    def desc(self):
        """Descripcion del objeto del servicio."""
        return self.__desc

    @overload
    def paths(self) -> list[list["ServiceObj"]]: ...
    @overload
    def paths(self, *, attr: str) -> list[list[Any]]: ...
    def paths(self, *, attr: str = None):
        """Busca los ServiceObj anidados y los devuelve como rutas, opcional los atributos."""
        if not attr is None and not hasattr(self, attr):
            raise AttributeError(f"en el ServiceObj no se ha encontrado el attributo '{attr}'")

        def _collect_obj(current: ServiceObj, path: list[ServiceObj]):
            paths = [path]
            for value in current.values():
                paths.extend(_walk_value(value, path))
            return paths

        def _walk_value(obj: ServiceObj, path: list[ServiceObj]):
            found = []
            if isinstance(obj, ServiceObj):
                value = obj if attr is None else getattr(obj, attr)
                found.extend(_collect_obj(obj, path + [value]))
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    found.extend(_walk_value(item, path))
            return found

        value = self if attr is None else getattr(self, attr)
        return _collect_obj(self, [value])

    def get(self, *names: str) -> Union["ServiceObj", None]:
        """Obtener el ServiceInfo por la ruta de nombres, sino lo encuentra devuelve None."""
        if not names:
            return None

        name = names[0]
        values = list(self.values())

        if not values:
            values = [self]

        for value in values:
            if isinstance(value, ServiceObj) and value.name == name:
                if names[1:]:
                    return value.get(*names[1:])
                return value
            if isinstance(value, (list, tuple)):
                values.extend(value)

        return None

    def __contains__(self, key):
        if isinstance(key, str):
            key = (key,)
        if isinstance(key, tuple):
            return not self.get(*key) is None
        return super().__contains__(key)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = (key,)
        if isinstance(key, tuple):
            item = self.get(*key)
            if not item is None:
                return item
        raise ServiceNotFound(f"no se ha encontrado el ServiceObj con la llave: '{key}'")

    def to_dict(self):
        """Devuleve un diccionario con las propiedades del servicio."""
        data = {"name": self.name}
        if self.type:
            data["type"] = self.type
        # if self.func:
        #     data["func"] = self.func.__name__
        if self.desc:
            data["desc"] = self.desc
        return data

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        func = self.func
        if func and callable(func):
            return func(*args, **kwargs)
        raise ServiceNotImplementedError("no existe una funcion implementada del servicio.")

    def info(self) -> dict[str, Union["ServiceObj", list["ServiceObj"]]]:
        """Crea un diccionario que muestra informacion de los servicios, segun el grupo."""
        info = {}

        for k, v in self.items():
            if isinstance(v, ServiceObj):
                v = v.to_dict()
            elif isinstance(v, (tuple, list)):
                v = [i.to_dict() if isinstance(i, ServiceObj) else i for i in v]
            elif isinstance(v, dict):
                v = {sk:sv.to_dict() if isinstance(sv, ServiceObj) else sv
                     for sk, sv in v.items()}
            info[k] = v

        if not info:
            info = self.to_dict()
        return info

    # abstract method
    async def exec(self, *args: P.args, **kwargs: P.kwargs) -> Never:
        """Ejecuta la funcion del ServiceObj, como metodo abstracto esto causa error por defecto."""
        raise ServiceNotImplementedError("no existe una funcion implementada del servicio.")

    async def run(self, *args: P.args, **kwargs: P.kwargs) -> ServiceResult[R]:
        """Corre el servicio si tiene una funcion implementada,
        sino lanza error: ServiceNotImplementedError."""
        try:
            return await self.exec(*args, **kwargs)
        except ServiceError as err:
            msg = ", ".join(err.args)
            return {
                "data": None,
                "type": err.__class__.__name__,
                "errs": msg
            }

class ServiceOptParameter(Generic[P, R], ServiceObj[Any, P, R]):
    """Crea un parametro de operaciones de los servicios."""

class ServiceOptReturn(Generic[P, R], ServiceOptParameter[P, R]):
    """Crea un return en operaciones de los servicios."""

class ServiceOperation(Generic[P, R], ServiceObj[ServiceOptParameter, P, R]):
    """Crea una operacion de un servicio."""

class Service(ServiceObj[ServiceOperation, ..., Any]):
    """Crea un grupo de operaciones de servicio."""

class ServicesGroup(ServiceObj[Service, ..., Any]):
    """Crea un grupo de servicios."""

class ServicesGroups(ServiceObj[ServicesGroup, ..., Any]):
    """Crea un conjunto de grupos de servicios."""
