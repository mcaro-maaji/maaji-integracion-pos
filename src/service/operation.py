"""Modulo para definir como se ejecutan las operaciones de los servicios."""

from typing import TypeVar, ParamSpec, Generic, Callable, Coroutine, AsyncGenerator, Any
from inspect import signature, iscoroutine
from .parameters import ServiceOptParameter, ServiceOptReturn
from .types import (
    ServiceResult,
    ServiceError,
    ServiceParamError,
    ServiceOperation as _ServiceOperation,
)

P = ParamSpec("P")
R = TypeVar("R")

def _opt_return_default(value):
    """Devolucion de servicio con el valor dado por la funcion del objecto ServiceOperacion."""

    if isinstance(value, type):
        type_name = value.__name__
    else:
        type_name = value.__class__.__name__

    return ServiceResult({
        "data": value,
        "type": type_name
    })

opt_return_default = ServiceOptReturn(_opt_return_default, name="default", type="type[object]")

class ServiceOperation(Generic[P, R], _ServiceOperation[P, R]):
    """Crea una operacion de un servicio."""
    __func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]
    __parameters: tuple[ServiceOptParameter, ...]
    __parameterskv: dict[str, ServiceOptParameter]
    __opt_return: ServiceOptReturn[..., R]

    def __init__(self,
                 func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]],
                 /,
                 *parameters: ServiceOptParameter | ServiceOptReturn,
                 name: str = None,
                 type: str = "",
                 desc: str = "",
                 parameterskv: dict[str, ServiceOptParameter] = None):
        name = name if name else func.__name__
        if parameterskv is None:
            parameterskv = {}
        opt_return = [i for i in parameters if isinstance(i, ServiceOptReturn)]
        parameters = [i for i in parameters if not isinstance(i, ServiceOptReturn)]
        opt_return = opt_return_default if not opt_return else opt_return[-1]

        params = {
            "parameters": parameters,
            "parameterskv": parameterskv,
            "return": opt_return
        }
        super().__init__(name=name, type=type, func=func, desc=desc, **params)
        self.__func = func
        self.__sig = signature(func)
        self.__parameters = tuple(parameters)
        self.__parameterskv = parameterskv
        self.__opt_return = opt_return

        self.repr_params = ", ".join([f"{p.name}: {p.type}" for p in parameters])
        self.repr_params = f"({self.repr_params})"
        self.repr_paramskv = ", ".join([f"{k}: {p.type}" for k, p in parameterskv.items()])
        self.repr_paramskv = f"({self.repr_paramskv})"
        self.repr_return = opt_return.type

    @property
    def func(self):
        return self.__func

    @property
    def sig(self):
        """Firma de la funcion de la operacion."""
        return self.__sig

    @property
    def parameters(self):
        """Parametros posicionales de la operacion del servicio."""
        return self.__parameters

    @property
    def parameterskv(self):
        """Parametros clave-valor de la operacion del servicio."""
        return self.__parameterskv

    @property
    def opt_return(self):
        """Devolucion de la operacion del servicio."""
        return self.__opt_return

    async def exec_args(self, *args: P.args) -> AsyncGenerator[ServiceResult, None]:
        """Executa el servicio de los parametros posicionales."""
        for param, arg in zip(self.parameters, args):
            try:
                result = await param.run(arg)
                errs = result.get("errs")
                if not errs is None:
                    raise ServiceParamError(errs)
                yield result
            except ServiceParamError as err:
                msg = "se espera argumentos de los parametros posicionales"
                msg += f": {self.repr_params}, {err}"
                raise ServiceParamError(msg) from err

    async def exec_kwargs(self, **kwargs: P.kwargs) -> AsyncGenerator[tuple[str, ServiceResult], None]:
        """Executa el servicio de los parametros clave-valor."""
        keys_kwargs = set(kwargs.keys()).intersection(self.parameterskv.keys())

        for key in keys_kwargs:
            param = self.parameterskv[key]
            arg = kwargs[key]

            try:
                result = await param.run(arg)
                errs = result.get("errs")
                if not errs is None:
                    raise ServiceParamError(errs)
                yield key, result
            except ServiceParamError as err:
                msg = "se espera argumentos de los parametros clave-valor"
                msg += f": {self.repr_paramskv}, {err}"
                raise ServiceParamError(msg) from err

    async def exec(self, *args: P.args, **kwargs: P.kwargs) -> ServiceResult[R]:
        args = [arg["data"] async for arg in self.exec_args(*args)]
        kwargs = {key: value["data"] async for key, value in self.exec_kwargs(**kwargs)}

        func = self.func
        len_args = len(self.parameters)
        msgerr = f"ha ocurrido un error en la operacion '{self.name}'"

        try:
            bound = self.sig.bind(*args,  **kwargs)
            bound.apply_defaults()
        except TypeError as err:
            if len(args) < len_args:
                msgerr += f", se esperaban {len_args} argumentos posicionales"
            else:
                msgerr += ", " + str(err)

            raise ServiceParamError(msgerr) from err

        try:
            return_arg = func(*bound.args, **bound.kwargs)
            if iscoroutine(return_arg):
                return_arg = await return_arg

            return await self.opt_return.run(return_arg)
        except Exception as err:
            msgerr += ", " + str(err)
            raise ServiceError(msgerr) from err
