"""Modulo para funciones como los objectos de los servicios."""

from typing import TypeVar, ParamSpec, overload, Callable, Coroutine, Any
from inspect import isfunction
from .parameters import ServiceOptParameter, ServiceOptReturn
from .operation import ServiceOperation
from .types import (
    Service,
    ServicesGroup,
    ServicesGroups
)

P = ParamSpec("P")
R = TypeVar("R")

class services:
    """Decoradores para crear los objectos de los servicios."""

    @overload
    @staticmethod
    def parameter(func: Callable[P, R], /) -> ServiceOptParameter[P, R]: ...

    @overload
    @staticmethod
    def parameter(func: Callable[P, Coroutine[Any, Any, R]], /) -> ServiceOptParameter[P, R]: ...

    @overload
    @staticmethod
    def parameter(*, name: str = "", type: str = "", desc: str = "") -> Callable[[Callable[P, R]], ServiceOptParameter[P, R]]: ...

    @overload
    @staticmethod
    def parameter(*, name: str = "", type: str = "", desc: str = "") -> Callable[[Coroutine[Any, Any, R]], ServiceOptParameter[P, R]]: ...

    @staticmethod
    def parameter(func: Callable[P, R] = None, *, name: str = None, type: str = "", desc: str = ""):
        """Crea un parametro de servicio."""

        def _decorator(func: Callable[P, R], /):
            nm = name if name else func.__name__
            dc = desc if desc else func.__doc__ or ""
            return ServiceOptParameter(func, name=nm, type=type, desc=dc)

        if func is None:
            return _decorator
        return _decorator(func)

    @overload
    @staticmethod
    def opt_return(func: Callable[P, R], /) -> ServiceOptReturn[P, R]: ...

    @overload
    @staticmethod
    def opt_return(func: Callable[P, Coroutine[Any, Any, R]], /) -> ServiceOptReturn[P, R]: ...

    @overload
    @staticmethod
    def opt_return(*, name: str = "", type: str = "", desc: str = "") -> Callable[[Callable[P, R]], ServiceOptReturn[P, R]]: ...

    @overload
    @staticmethod
    def opt_return(*, name: str = "", type: str = "", desc: str = "") -> Callable[[Callable[P, Coroutine[Any, Any, R]]], ServiceOptReturn[P, R]]: ...

    @staticmethod
    def opt_return(func: Callable[P, R] = None, *, name: str = None, type: str = "", desc: str = ""):
        """Crea una devolucion del servicio."""

        def _decorator(func: Callable[P, R], /):
            nm = name if name else func.__name__
            dc = desc if desc else func.__doc__ or ""
            return ServiceOptReturn(func, name=nm, type=type, desc=dc)

        if func is None:
            return _decorator
        return _decorator(func)

    @overload
    @staticmethod
    def operation(*parameters: ServiceOptParameter | ServiceOptReturn,
                  **parameterskv: ServiceOptParameter) -> Callable[[Callable[P, R]], ServiceOperation[P, R]]: ...

    @overload
    @staticmethod
    def operation(*parameters: ServiceOptParameter | ServiceOptReturn,
                  **parameterskv: ServiceOptParameter) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], ServiceOperation[P, R]]: ...

    @overload
    @staticmethod
    def operation(func: Callable[P, R], /) -> ServiceOperation[P, R]: ...

    @overload
    @staticmethod
    def operation(func: Callable[P, Coroutine[Any, Any, R]], /) -> ServiceOperation[P, R]: ...

    @staticmethod
    def operation(_func: Callable[P, R] = None,
                  /,
                  *paramters: ServiceOptParameter | ServiceOptReturn,
                  **parameterskv: ServiceOptParameter):

        """Crea una operacion de servicio."""

        def _decorator(func: Callable[P, R], /):
            name = func.__name__
            # type = f"ServiceOperation[{name}]"
            type = ""
            desc = func.__doc__ or ""

            params_as_args = [_func]
            if not isfunction(_func):
                params_as_args.extend(paramters)
            else:
                params_as_args = paramters

            return ServiceOperation(func,
                                    *params_as_args,
                                    name=name,
                                    type=type,
                                    desc=desc,
                                    parameterskv=parameterskv)

        if _func is None or not isfunction(_func):
            return _decorator
        return _decorator(_func)

    @staticmethod
    def service(name: str, /, *operations: ServiceOperation, desc: str = ""):
        """Crea un servicio que agrupa operaciones."""
        return Service(name=name, desc=desc, operations=operations)

    @staticmethod
    def group(name: str, /, *services: Service, desc: str = ""):
        """Crea un grupo de servicios."""
        return ServicesGroup(name=name, desc=desc, services=services)

    @staticmethod
    def groups(name: str, /, *groups: ServicesGroup, desc: str = ""):
        """Crea un conjunto de grupos de servicios."""
        return ServicesGroups(name=name, desc=desc, groups=groups)
