"""
Modulo para manejar los datos IO de forma general para toda la aplicacion.

- Multiples soporte para la lectura y escritura de los datos.
- Multiples modos en como ingresa y sale la informacion.
"""

from pathlib import Path
from typing import Literal, TypeGuard
from os import PathLike
from io import IOBase, BytesIO
from quart.datastructures import FileStorage
from pandas import (
    DataFrame,
    ExcelFile,
    read_csv,
    read_excel,
    read_json,
    read_clipboard
)
from pandas.io.clipboard import clipboard_get, clipboard_set

DataIO = str | bytes | PathLike | IOBase | ExcelFile | FileStorage
SupportDataIO = Literal["object", "csv", "excel", "json", "clipboard"]
ListSupportDataIO: list[SupportDataIO] = ["object", "csv", "excel", "json", "clipboard"]
REPR_SUPPORT_DATAIO = "'" + "'|'".join(ListSupportDataIO) + "'"

ModeDataIO = Literal["object", "raw", "path", "ftp", "buffer", "request"]
ListModeDataIO: list[ModeDataIO] = ["object", "raw", "path", "ftp", "buffer", "request"]
REPR_MODE_DATAIO = "'" + "'|'".join(ListModeDataIO) + "'"

def is_dataio(dataio) -> TypeGuard[DataIO]:
    """Comprobar de que el valor sea uno soportado para ser gestionado por la clase BaseDataIO."""
    dataio_types = (str, bytes, PathLike, IOBase, ExcelFile, FileStorage, DataFrame)
    return isinstance(dataio, dataio_types)

def transform_dataio(dataio: DataIO | None,
                     support: SupportDataIO,
                     mode: ModeDataIO,
                     **kwargs: ...):
    """Transforma y verifica el DataIO segun las condiciones/mezclas del soporte y modo."""

    if support == "clipboard" and dataio is None:
        dataio = ""

    if mode == "raw":
        if not isinstance(dataio, IOBase):
            if isinstance(dataio, str):
                raw_bytes = dataio.encode(kwargs.get("encoding", "utf-8"))
                dataio = BytesIO(raw_bytes)
            elif not isinstance(dataio, bytes):
                raise TypeError("el valor debe ser de tipo string|bytes")
    elif mode == "path":
        if support == "clipboard":
            path = Path(str(clipboard_get()))
            dataio = path

        if not isinstance(dataio, (str, bytes, PathLike)):
            raise TypeError("el valor debe ser de tipo PathLike'")

    # TODO: mode == "ftp" -> buffer

    return dataio

class BaseDataIO:
    """Clase para la gestion de datos con soporte a diferentes fuentes de entradas."""
    __source: DataIO | None
    __destination: DataIO | None
    __support: SupportDataIO
    __mode: ModeDataIO
    __data: DataFrame

    def __init__(self,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object"):
        """Crea un nuevo set de datos manipulable con pandas.DataFrame."""
        self.source = source
        self.destination = destination
        self.support = support
        self.mode = mode

    @property
    def source(self):
        """Origen de los datos."""
        return self.__source

    @source.setter
    def source(self, value):
        if is_dataio(value) or value is None:
            self.__source = value
        else:
            raise TypeError("el valor de 'source' debe ser de tipo DataIO.")

    @property
    def destination(self):
        """Guarda un destino para los datos de tipo DataIO o nulo sin un destino definido."""
        return self.__destination

    @destination.setter
    def destination(self, value):
        if is_dataio(value) or value is None:
            self.__destination = value
        else:
            raise TypeError("el valor de 'destination' debe ser de tipo DataIO.")

    @property
    def support(self):
        """Soporte de BaseDataIO."""
        return self.__support

    @support.setter
    def support(self, value):
        if value not in ListSupportDataIO:
            msg = "se espera alguno de estos valores: " + REPR_SUPPORT_DATAIO
            raise ValueError(msg)
        self.__support = value

    @property
    def mode(self):
        """Modo de BaseDataIO."""
        return self.__mode

    @mode.setter
    def mode(self, value):
        if value not in ListModeDataIO:
            msg = "se espera alguno de estos valores: " + REPR_MODE_DATAIO
            raise ValueError(msg)
        self.__mode = value

    @property
    def data(self):
        """DataFrame de BaseDataIO."""
        return self.__data

    @data.setter
    def data(self, value):
        if not isinstance(value, DataFrame):
            raise TypeError("se espera un tipo DataFrame en BaseDataIO")
        self.__data = value

    def load(self, **kwargs: ...):
        """Carga el set de datos extrayendo la informacion del origen."""

        source = transform_dataio(self.source, self.support, self.mode, **kwargs)

        if not is_dataio(source):
            raise TypeError("el valor de 'source' debe ser de tipo DataIO.")

        if self.support == "csv":
            self.__data = read_csv(source, **kwargs)
        elif self.support == "excel":
            self.__data = read_excel(source, **kwargs)
        elif self.support == "json":
            self.__data = read_json(source, **kwargs)
        elif self.support == "clipboard":
            if self.mode == "path" and isinstance(source, Path):
                if not source.is_file():
                    msg = "no se ha encontrado el archivo en la ruta: " + str(source)
                    raise FileNotFoundError(msg)

                with open(source, encoding="utf-8") as file:
                    text = file.read()
                    clipboard_set(text)

            self.__data = read_clipboard(**kwargs)
        else:
            self.__data = DataFrame(source, **kwargs)

    def save(self,
             support: SupportDataIO = None,
             mode: ModeDataIO = None,
             **kwargs: ...) -> DataIO | None:
        """
        Envia la informacion a un destino o devuelve un valor, segun los parametros.
        si el soporte es 'object' este devuelve un string con los datos.
        """
        if not support:
            support = self.support
        if not mode:
            mode = self.mode

        destination = transform_dataio(self.destination, support, mode, **kwargs)
        data_returned: str | None = None

        if not is_dataio(destination):
            raise TypeError("el valor de 'destination' debe ser de tipo DataIO.")

        if support == "csv":
            data_returned = self.data.to_csv(destination, **kwargs)
        elif support == "excel":
            data_returned = self.data.to_excel(destination, **kwargs)
        elif support == "json":
            data_returned = self.data.to_json(destination, **kwargs)
        elif support == "clipboard":
            self.data.to_clipboard(**kwargs)
            return destination
        else:
            data_returned = self.data.to_string(destination, **kwargs)

        return data_returned or destination
