"""Modulo para definir como se ejecutan las operaciones de los servicios."""

from typing import Any
from inspect import signature, iscoroutine
from .types import (
    ServiceParams,
    ServiceResult,
    is_service_result,
    ServiceError,
    ServiceParamError,
    ServiceOptReturn,
    ServiceOptParameter,
    ServiceOperation as AbsServiceOperation,
)

def _return_default(_) -> ServiceResult:
    return {
        "data": None,
        "type": "None"
    }

return_default = ServiceOptReturn(
    name="return",
    type="{'data': None, 'type': string}",
    func=_return_default
)

class ServiceOperation(AbsServiceOperation):
    """Crea una operacion de un servicio."""
    __param_args: list[ServiceOptParameter] = None
    __param_kwargs: dict[str, ServiceOptParameter] = None
    __param_return: ServiceOptReturn = None

    def exec_lookup_params(self):
        """Busca y organiza los parametros de la operacion."""
        self.__param_args = []
        self.__param_kwargs = {}
        self.__param_return = return_default

        for params in self.values():
            if isinstance(params, (list, tuple)):
                for param in params:
                    if isinstance(param, ServiceOptParameter):
                        self.__param_args.append(param)
                    else:
                        msg = "el parametro debe ser de tipo: 'ServiceOptParameter'"
                        raise ServiceParamError(msg)
            elif isinstance(params, ServiceOptReturn) and not params.func is None:
                self.__param_return = params
            elif isinstance(params, dict):
                msg = "{} de los parametros key-value deben ser de tipo: '{}'"
                for key, value in params.items():
                    if not isinstance(key, str):
                        raise ServiceParamError(msg.format("las llaves", "string"))
                    if not isinstance(value, ServiceOptParameter):
                        raise ServiceParamError(msg.format("los valores", "ServiceOptParameter"))
                self.__param_kwargs.update(params)
            else:
                raise ServiceParamError(f"parametros no validos: '{params}'")

    @property
    def param_args(self):
        """Contiene los parametros de la operacion."""
        if self.__param_args is None:
            self.exec_lookup_params()
        return self.__param_args

    @property
    def param_kwargs(self):
        """Contiene los parametros key-value de la operacion."""
        if self.__param_kwargs is None:
            self.exec_lookup_params()
        return self.__param_kwargs

    @property
    def param_return(self):
        """Contiene el return de la operacion."""
        if self.__param_return is None:
            self.exec_lookup_params()
        return self.__param_return

    def exec_args(self, *args: Any):
        """Ejecuta las funciones de los parametros."""
        result_args = []

        for arg, param in zip(args, self.param_args):
            if not param.func is None:
                try:
                    result_args.append(param.func(arg))
                except Exception as err:
                    msg = f"ha ocurrido un error en el parametro '{param.name}', {err}"
                    raise ServiceParamError(msg) from err
            else:
                result_args.append(None)

        return tuple(result_args)

    def exec_kwargs(self, **kwargs: Any):
        """Ejecuta las funciones de los parametros de tipo llave y valor."""
        result_kwargs = {}
        keys_kwargs = set(kwargs.keys()).intersection(self.param_kwargs.keys())

        for key in keys_kwargs:
            arg = kwargs[key]
            param = self.param_kwargs[key]

            if not param.func is None:
                try:
                    result_kwargs[key] = param.func(arg)
                except Exception as err:
                    msg = f"ha ocurrido un error en el parametro key-value '{param.name}', {err}"
                    raise ServiceParamError(msg) from err
            else:
                result_kwargs[key] = None

        return result_kwargs

    def exec_return(self, return_arg: Any):
        """Ejecuta la funcion del retorno de la operacion."""

        try:
            result_return = self.param_return.func(return_arg)
        except Exception as err:
            msg = f"ha ocurrido un error en el return '{self.param_return.name}', {err}"
            raise ServiceParamError(msg) from err

        if not is_service_result(result_return):
            msg = f"el valor del return debe ser de tipo ServiceResult: '{self.param_return.name}'"
            raise ServiceParamError(msg)

        return result_return

    async def exec(self, params: ServiceParams = None) -> ServiceResult:
        if self.func is None:
            super().exec(params)

        self.exec_lookup_params()

        if params is None:
            args = tuple()
            kwargs = {}
        else:
            args = params["parameters"]
            kwargs = params.get("parameters_kv", {})

        args = self.exec_args(*args)
        kwargs = self.exec_kwargs(**kwargs)
        func = self.func # property no callable Pylint(E1102:not-callable)
        sig = signature(func)

        try:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
        except TypeError as err:
            msg = str(err)
            msg_required_arg = "missing a required argument: "
            if msg.startswith(msg_required_arg):
                msg_param = msg[len(msg_required_arg):]
                msg = f"el argumento es requerido en el parametro: {msg_param}"
            raise ServiceParamError(msg) from err

        try:
            result = func(*bound.args, **bound.kwargs)
            return_arg = await result if iscoroutine(result) else result
        except Exception as err:
            msg = f"ha ocurrido un error en la ejeccion de la operacion '{self.name}', {err}"
            raise ServiceError(msg) from err

        result_return = self.exec_return(return_arg)
        return result_return
