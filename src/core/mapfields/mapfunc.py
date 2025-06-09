"""Modulo para asignar una funcion que homologue los campos."""

from typing import Callable
from enum import StrEnum
from re import compile as re_compile

class MapFieldFunc(StrEnum):
    """Nombre clave de las funciones basicas como criterios de homologacion de datos."""
    EQ = "equal"
    DI = "diferent"
    CO = "content"
    NC = "no content"
    PF = "prefix"
    SF = "suffix"
    RE = "regex"

    def cb(self, data: dict[str, str], default="") -> Callable[[str], str]:
        """Devuelve un callback de la funcion MapField para homologar datos."""

        if self == MapFieldFunc.EQ:
            def callback(value: str):
                if value in data:
                    return data[value]
                return default
        elif self == MapFieldFunc.DI:
            def callback(value: str):
                if value not in data and len(data) > 0:
                    return next(iter(data.values()), default)
                return default
        elif self == MapFieldFunc.CO:
            def callback(value: str):
                for k, v in data.items():
                    if value in k:
                        return v
                return default
        elif self == MapFieldFunc.NC:
            def callback(value: str):
                for k, v in data.items():
                    if value not in k:
                        return v
                return default
        elif self == MapFieldFunc.PF:
            def callback(value: str):
                for k, v in data.items():
                    if k.startswith(value):
                        return v
                return default
        elif self == MapFieldFunc.SF:
            def callback(value: str):
                for k, v in data.items():
                    if k.endswith(value):
                        return v
                return default
        elif self == MapFieldFunc.RE:
            def callback(value: str):
                for k, v in data.items():
                    patter = re_compile(k)
                    if patter.search(value):
                        return v
                return default
        else:
            def callback(__value: str):
                return default

        return callback
