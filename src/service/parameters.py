"""Modulo para construir la logica de los parametros en los servicios."""

from typing import TypeVar, ParamSpec, Generic, Callable, Coroutine, Any
from inspect import Signature, signature, iscoroutine
from .types import (
    ServiceParamError,
    ServiceOptParameter as _ServiceOptParameter,
    ServiceResult,
    is_service_result
)

P = ParamSpec("P")
R = TypeVar("R")

class ServiceOptParameter(Generic[P, R], _ServiceOptParameter[P, R]):
    """Crea un parametro de operaciones de los servicios."""
    __func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]
    __sig: Signature

    def __init__(self,
                 func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]],
                 *,
                 name: str = None,
                 type: str = "",
                 desc: str = ""):
        name = name if name else func.__name__
        super().__init__(name=name, type=type, func=func, desc=desc)
        self.__func = func
        self.__sig = signature(func)

    @property
    def func(self):
        return self.__func

    @property
    def sig(self):
        """Firma de la funcion del parametro."""
        return self.__sig

    async def exec(self, *args: P.args, **kwargs: P.kwargs) -> ServiceResult[R]:
        func = self.func
        try:
            bound = self.sig.bind(*args, **kwargs)
            bound.apply_defaults()
        except TypeError as err:
            msg = f"se esperaba argumentos validos para el parametro '{self.name}: {self.type}'"
            raise ServiceParamError(msg) from err
        try:
            result = func(*bound.args, **bound.kwargs)
            if iscoroutine(result):
                result = await result

            return {
                "data": result,
                "type": "ServiceOptParameter"
            }
        except Exception as err:
            msg = f"ha ocurrido un error en el parametro '{self.name}', {err}"
            raise ServiceParamError(msg) from err

class ServiceOptReturn(Generic[P, R], ServiceOptParameter[P, ServiceResult[R]]):
    """Crea un return en operaciones de los servicios."""

    async def exec(self, *args: P.args, **kwargs: P.kwargs) -> ServiceResult[R]:
        func = self.func
        try:
            bound = self.sig.bind(*args, **kwargs)
            bound.apply_defaults()
        except TypeError as err:
            return_type = self.type if self.type else "None"
            msg = f"se esperaba argumentos validos para el return '{self.name} -> {return_type}'"
            raise ServiceParamError(msg) from err
        try:
            result = func(*bound.args, **bound.kwargs)
            if iscoroutine(result):
                result = await result

            if not is_service_result(result):
                msg = f"el valor del return debe ser de tipo ServiceResult: '{self.name}'"
                raise ServiceParamError(msg)
            return result
        except Exception as err:
            msg = f"ha ocurrido un error al calcular el retorno del servicio '{self.name}', {err}"
            raise ServiceParamError(msg) from err
