"""Modulo para crear un gestionador de datos, como si fuera un cache."""

from __future__ import annotations
from typing import TypeVar, Generic, Callable, overload, Literal
from collections import UserDict
from datetime import datetime, timedelta
from uuid import UUID, uuid4

VT = TypeVar("VT")

class DataStore(Generic[VT], UserDict[UUID, VT]):
    """Gestiona capacidad de espacio de los datos."""
    cache: dict[UUID, DataStore] = {}
    __id: UUID
    __create_at: datetime
    __init_at: datetime
    __persistent: list[UUID]
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
        self.__init_at = datetime.now()
        self.__id = uuid4()
        self.__persistent = []

        super().__init__()
        super().update({uuid4(): item for item in args})
        type(self).cache[self.__id] = self

    @property
    def id(self):
        """ID del DataStore."""
        return self.__id

    @property
    def create_at(self):
        """Fecha de creacion del DataStore."""
        return self.__create_at

    @property
    def init_at(self):
        """Fecha de inicio en el que transcurre el DataStore."""
        return self.__init_at

    @property
    def persistent(self):
        """IDs que no se eliminan."""
        return self.__persistent

    @property
    def length(self):
        """Cantidad permitida de elementos del DataStore."""
        return len(self)

    @property
    def size(self):
        """Tamaño actual del DataStore."""
        return sum(self.calc_size(item) for item in self.values())

    @property
    def time_elapsed(self):
        """Tiempo transcurrido desde el inicial al actual del DataStore."""
        return datetime.now() - self.init_at

    def count_items_expired(self):
        count_items = int(self.time_elapsed * self.max_length / self.max_duration)
        if count_items >= self.max_length:
            return self.max_length
        return count_items

    def popitems_expired(self):
        """Elimina los ultimos elementos si ha expirado el tiempo."""
        count_popitems = self.length - (self.max_length - self.count_items_expired())
        if count_popitems > 0:
            for _ in range(count_popitems):
                key, value = self.popitem()
                if key in self.persistent:
                    self[key] = value

    def reset_init(self):
        """Reinicia la fecha de inicio a la actual para reutilizar el DataStore."""
        self.__init_at = datetime.now()

    def is_expired(self):
        """Comprueba que el DataStore haya expirado."""
        return datetime.now() > self.init_at + self.max_duration

    def __getitem__(self, key):
        try:
            data = super().__getitem__(key)
        except KeyError as err:
            msg = f"no se ha encontrado el elemento con el ID: '{key}'"
            raise MemoryError(msg) from err
        return data

    def get(self, key: UUID, default: VT = None):
        try:
            return self[key]
        except MemoryError:
            return default

    def __setitem__(self, key, item):
        if key not in self and self.length + 1 > self.max_length:
            raise MemoryError(f"fuera de capacidad maxima de elementos: {self.max_length}")

        total_max_size = self.max_size * self.max_length

        if self.size + self.calc_size(item) > total_max_size:
            raise MemoryError(f"fuera de capacidad maxima de tamaño: {total_max_size:.3f}")

        super().__setitem__(key, item)

    def append(self, item: VT, *, force: bool = False):
        """Agrega un elemento Data, devuelve el UUID,
        con force activado despeja espacio para el nuevo item."""
        uuid = uuid4()
        try:
            self[uuid] = item
        except MemoryError as err:
            if not force:
                raise err

            total_max_size = self.max_size * self.max_length
            size_item = self.calc_size(item)
            size_p_items = sum(self.calc_size(v) for k, v in self.items() if k in self.persistent)

            if size_item > total_max_size - size_p_items:
                raise err

            dump_size = self.size - size_p_items - size_item
            for _ in range(self.length):
                key, value = self.popitem()
                if key in self.persistent:
                    self[key] = value
                    continue

                if self.size <= dump_size:
                    break
            self[uuid] = item
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
                datastore.popitems_expired()

    @overload
    @classmethod
    def get_datastore(cls, idstore: UUID, err: Literal["raise"] = ...) -> DataStore: ...
    @overload
    @classmethod
    def get_datastore(cls, idstore: UUID, err: Literal["ignore"] = ...) -> DataStore | None: ...
    @classmethod
    def get_datastore(cls, idstore: UUID, err: Literal["raise", "ignore"] = "raise"):
        """Comprueba que exista un DataStore en cache, si no existe lanza error."""
        datastore = cls.cache.get(idstore)
        if datastore is None and err == "raise":
            raise KeyError(f"no se ha encontrado el DataStore con el ID: '{idstore}'")
        return datastore
