"""Modulo para crear un gestionador de datos, como si fuera un cache."""

from typing import TypeVar, Generic, Callable
from collections import UserDict
from datetime import datetime, timedelta
from uuid import UUID, uuid4

VT = TypeVar("VT")

class DataStore(Generic[VT], UserDict[UUID, VT]):
    """Gestiona capacidad de espacio de los datos."""
    cache: dict[UUID, "DataStore"] = {}
    __create_at: datetime
    maxsize: int
    maxlen: int
    maxtime: timedelta
    getsize: Callable[[VT], int]

    def __init__(self, *args: VT, maxsize: int, maxlen: int = None, maxtime: timedelta = None):
        if not maxlen:
            maxlen = len(args)
        args = args[0:maxlen]

        if not maxtime:
            maxtime = timedelta(minutes=10)

        self.maxlen = maxlen
        self.maxsize = maxsize
        self.maxtime = maxtime
        self.getsize = lambda __value: self.maxsize
        self.__create_at = datetime.now()

        super().__init__()
        super().update({uuid4(): item for item in args})
        type(self).cache[uuid4()] = self

    @property
    def create_at(self):
        """Fecha de creacion del DataStore."""
        return self.__create_at

    @property
    def length(self):
        """Cantidad actual de elementos del DataStore."""
        return len(self)

    @property
    def size(self):
        """Tamaño actual del DataStore."""
        size = 0
        for item in self.values():
            size += self.getsize(item)
        return size

    @property
    def time_elapsed(self):
        """Tiempo transcurrido actual del DataStore."""
        return datetime.now() - self.create_at

    __last_expected_items_deleted = 0

    def __is_item_to_pop(self):
        expected_items_deleted = int(self.time_elapsed / self.maxtime)
        if expected_items_deleted > self.__last_expected_items_deleted:
            self.__last_expected_items_deleted = expected_items_deleted
            return True
        return False

    def time_pop(self, *, key: UUID, default: VT = None):
        """Elimina un elemento si ha expirado el tiempo."""
        if self.__is_item_to_pop():
            return UserDict.pop(self, key, default=default)
        return default

    def time_popitem(self) -> tuple[UUID, VT]:
        """Elimina el ultimo elemento si ha expirado el tiempo."""
        if self.__is_item_to_pop():
            return UserDict.popitem(self)
        return None

    def time_clear(self):
        """Funcion en main loop, elimina el ultimo elemento si ha expirado el tiempo."""
        self.time_popitem()

    def __getitem__(self, key):
        try:
            data = super().__getitem__(key)
        except KeyError as err:
            msg = f"no se ha encontrado el elemento con la llave UUID: '{key}'"
            raise MemoryError(msg) from err
        self.time_clear()
        return data

    def get(self, key: UUID, default: VT = None):
        try:
            return self[key]
        except MemoryError:
            return default

    def __setitem__(self, key, item):
        self.time_clear()

        if key not in self and self.length + 1 > self.maxlen:
            raise MemoryError(f"fuera de capacidad maxima de elementos: '{self.maxlen}'")

        total_maxsize = self.maxsize * self.maxlen
        if self.size + self.getsize(item) > total_maxsize:
            raise MemoryError(f"fuera de capacidad maxima de tamaño: '{total_maxsize}'")

        super().__setitem__(key, item)

    def append(self, value: VT):
        """Agrega un elemento Data, devuelve el UUID."""
        uuid = uuid4()
        self[uuid] = value
        return uuid

    def update(self, other=None, /, **kwargs):
        if not other is None:
            if isinstance(other, dict):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def extend(self, *args: VT):
        """Agregar varios elementos en el DataStore."""
        for item in args:
            self.append(item)

    @classmethod
    def cache_clear(cls):
        """Funcion en un main loop para ir limpiando la cache."""
        for datastore in cls.cache.values():
            if datastore:
                datastore.time_clear()
