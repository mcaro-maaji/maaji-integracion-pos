"""Modulo para controlar los archivos JSON."""

import json
from typing import LiteralString, TypeVar
from pathlib import Path
from dataclasses import is_dataclass, asdict as dataclass_asdict
from .typing import FilePath, ReadBuffer

T = TypeVar("T")

def from_json(source: FilePath | LiteralString | ReadBuffer | T) -> dict | list:
    """Forma util de leer de diferentes formas la informacion en JSON."""

    data = None
    if is_dataclass(source):
        data = dataclass_asdict(source)
    if isinstance(source, str):
        if Path(source).is_file():
            with open(source, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.loads(source)
    elif hasattr(source, "read"):
        data = json.load(source)
    elif isinstance(source, (list, tuple, set, dict)):
        data = source
    else:
        raise TypeError("El valor 'source' es de un tipo incompatible para JSON.")

    return data
