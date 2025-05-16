"""Modulo para crear un gestionador de datos, como si fuera un cache."""

from typing import TypeVar, Generic, Callable, overload
from collections import UserDict
from datetime import datetime, timedelta
from uuid import UUID, uuid4

VT = TypeVar("VT")

class DataStore(Generic[VT], UserDict[UUID, VT]):
    """Gestiona capacidad de espacio de los datos."""
    cache: dict[UUID, "DataStore"] = {}
    __create_at: datetime
    max_length: int
    max_size: int
    max_duration: timedelta
    calc_size: Callable[[VT], int]

    @overload
    def __init__(self, /, max_length = 1, max_size = 1, max_duration: timedelta = None): ...
    @overload
    def __init__(self, *args: VT, max_size = 1, max_duration: timedelta = None): ...
    def __init__(self, *args: VT, max_length = 1, max_size = 1, max_duration: timedelta = None):
        if max_length <= 0:
            max_length = 1

        if args:
            max_length = len(args)
        else:
            args = args[0:max_length]

        if max_size <= 0:
            max_size = 1

        if not max_duration:
            max_duration = timedelta(hours=1)

        self.max_length = max_length
        self.max_size = max_size
        self.max_duration = max_duration
        self.calc_size = lambda _: self.max_size
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
        """Cantidad permitida de elementos del DataStore."""
        return len(self)

    @property
    def size(self):
        """Tamaño actual del DataStore."""
        size = 0
        for item in self.values():
            size += self.calc_size(item)
        return size

    @property
    def time_elapsed(self):
        """Tiempo transcurrido actual del DataStore."""
        return datetime.now() - self.create_at

    def __count_expired_items(self):
        max_duration_per_item = self.max_duration / self.max_length
        count_expired_items = self.time_elapsed / max_duration_per_item
        count_expired_items = int(count_expired_items)
        if count_expired_items > self.length:
            return self.length
        return count_expired_items

    def pop_expired_items(self):
        """Elimina los ultimos elementos si ha expirado el tiempo."""
        count_expired_items = self.__count_expired_items()
        if count_expired_items:
            for _ in range(count_expired_items):
                self.popitem()

    def __getitem__(self, key):
        try:
            data = super().__getitem__(key)
        except KeyError as err:
            msg = f"no se ha encontrado el elemento con la llave UUID: '{key}'"
            raise MemoryError(msg) from err
        return data

    def get(self, key: UUID, default: VT = None):
        try:
            return self[key]
        except MemoryError:
            return default

    def __setitem__(self, key, item):
        if key not in self and self.length + 1 > self.max_length:
            raise MemoryError(f"fuera de capacidad maxima de elementos: '{self.max_length}'")

        total_max_size = self.max_size * self.max_length
        if self.size + self.calc_size(item) > total_max_size:
            raise MemoryError(f"fuera de capacidad maxima de tamaño: '{total_max_size}'")

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
        uuids: list[UUID] = []
        for item in args:
            uuids.append(self.append(item))
        return uuids

    @classmethod
    def clear_cache(cls):
        """Funcion en un main loop para ir limpiando la cache."""
        for datastore in cls.cache.values():
            if datastore:
                datastore.pop_expired_items()
