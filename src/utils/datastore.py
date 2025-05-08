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
    maxitems: int
    maxtime: timedelta
    getsize: Callable[[VT], int]

    def __init__(self, *args: VT, maxsize: int, maxitems: int = None, maxtime: timedelta = None):
        if not maxitems:
            maxitems = len(args)
        args = args[0:maxitems]

        if not maxtime:
            maxtime = timedelta(minutes=10)

        self.maxitems = maxitems
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
    def maxtime_total(self):
        """Obtener la duracion del DataStore."""
        return self.maxtime * self.maxitems

    @property
    def current_size(self):
        """Obtener el tamaño total actual de DataStore."""
        size = 0
        for item in self.values():
            size += self.getsize(item)
        return size

    @property
    def maxsize_total(self):
        """Obtener el tamaño estimado: maxsize * maxitems."""
        return self.maxsize * self.maxitems

    def time_pop(self, *, key: UUID, time: datetime = None):
        """Elimina un elemento segun la diferencia entre el tiempo y desde que se creo."""
        if time >= (self.create_at + self.maxtime):
            return self.pop(key, None)
        return None

    def time_popitem(self, time: datetime = None):
        """Elimina el ultimo elemento segun la diferencia entre el tiempo y desde que se creo."""
        if time >= (self.create_at + self.maxtime):
            return self.popitem()
        return None

    def time_clear(self):
        """Elimina los elementos segun la diferencia entre el tiempo actual y desde que se creo."""
        self.time_popitem(datetime.now())

    def __getitem__(self, key):
        data = super().__getitem__(key)
        self.time_clear()
        return data

    def get(self, key: UUID, default: VT = None):
        data = super().get(key, default)
        self.time_clear()
        return data

    def __setitem__(self, key, item):
        self.time_clear()

        if key not in self and len(self) + 1 > self.maxitems:
            raise MemoryError(f"fuera de capacidad maxima de elementos: {self.maxitems}")
        if self.current_size + self.getsize(item) > self.maxsize_total:
            raise MemoryError(f"fuera de capacidad maxima de tamaño: {self.maxsize_total}")

        super().__setitem__(key, item)

    def append(self, value: VT):
        """Agrega un elemento Data, devuelve el UUID."""
        uuid = uuid4()
        self[uuid] = value
        return uuid

    def update(self, *args: tuple[UUID, VT]) -> None:
        for key, value in args:
            self[key] = value

    def extend(self, *args: VT):
        """Agregar varios elementos en el DataStore."""
        for item in args:
            self.append(item)

    @classmethod
    def cache_clear(cls):
        """Funcion en un main loop para ir limpiando la cache."""
        for datastore  in cls.cache.values():
            if datastore:
                datastore.time_clear()
