"""Modulo para de tipado"""

from typing import Protocol, TypeVar, Iterator, Union
from os import PathLike

# filenames and file-like-objects
AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)
AnyStr_contra = TypeVar("AnyStr_contra", str, bytes, contravariant=True)
FilePath = Union[str, PathLike[str]]

class BaseBuffer(Protocol):
    @property
    def mode(self) -> str:
        ...

    def seek(self, __offset: int, __whence: int = ...) -> int:
        ...

    def seekable(self) -> bool:
        ...

    def tell(self) -> int:
        ...


class ReadBuffer(BaseBuffer, Protocol[AnyStr_co]):
    def read(self, __n: int = ...) -> AnyStr_co:
        ...

class ReadCsvBuffer(ReadBuffer[AnyStr_co], Protocol):
    def __iter__(self) -> Iterator[AnyStr_co]:
        ...

    def fileno(self) -> int:
        ...

    def readline(self) -> AnyStr_co:
        ...

    @property
    def closed(self) -> bool:
        ...
