"""Modulo para organizar la inforamcion de los clientes segun el Sistema POS."""

from typing import Literal, TypeVar, Generic
from pandas import DataFrame, ExcelFile, Series, Index, MultiIndex
from core.mapfields import MapFields
from utils.typing import FilePath, ReadBuffer, ReadCsvBuffer
from .clients import Clients
from .fields import ClientField

_K = TypeVar("_K", bound=str, covariant=True) # key primary

class ClientsPOS(Generic[_K], Clients):
    """Clientes que se manejan segun el sistema pos."""
    __mapfields: MapFields[_K, ClientField]
    __data_pos: DataFrame

    def __init__(self,
                 filepath_or_buffer: FilePath | ReadBuffer | ExcelFile | ReadCsvBuffer,
                 *,
                 ftype: Literal["excel", "csv", "json"] = "csv",
                 delimiter="|",
                 encoding="utf-8",
                 mapfields: MapFields[_K, ClientField]):
        super().__init__(filepath_or_buffer, ftype=ftype, delimiter=delimiter, encoding=encoding)
        self.__mapfields = mapfields
        self.__data_pos = self.data.copy()
        self.data = DataFrame(
            columns=self.data.columns.copy(),
            index=self.data.index.copy(),
            dtype=str
        )
        self.data.fillna("", inplace=True)

    @property
    def data_pos(self):
        """DataFrame de los clientes en el POS."""
        return self.__data_pos

    @data_pos.setter
    def data_pos(self, value: DataFrame):
        """Establecer un nuevo DataFrame de clientes en el POS."""

        if not isinstance(value, DataFrame):
            raise TypeError("el valor no es un tipo DataFrame.")
        self.__data_pos = value

    @property
    def mapfields(self):
        """Mapeo de los campos y homolacion de los datos."""
        return self.__mapfields

    def no_match_fields(self) -> set[tuple[_K, ClientField]]:
        mapfields = super().no_match_fields()
        set_fields = set()

        for mapfield in mapfields:
            fields = self.mapfields[mapfield]
            for field in fields:
                set_fields.add((field, mapfield))
            if not fields:
                set_fields.add((None, mapfield))
        return set_fields

    def incorrect_fields(self):
        incorrect_list = [i for i in self.data_pos if i not in self.mapfields.fields_1]
        return set(incorrect_list)

    def sort_fields(self, fields: set[_K] = None):
        map_fields = fields if fields else set(str(mf) for mf in self.mapfields.fields_1)
        map_fields = list(map_fields)
        self.data_pos = self.data_pos[map_fields]
        super().sort_fields()

    def fix(self, data: dict[tuple[_K, ClientField], Series]):
        data_fields = {k[0]: v for k, v in data.items()}
        data_mapfields: dict[ClientField, Series] = {}

        for (field, mapfield), value in data.items():
            if (field, mapfield) in self.mapfields:
                callback = self.mapfields[field, mapfield].lookup()
                if callback:
                    value = value.apply(callback)

            data_mapfields[mapfield] = value

        self.data_pos.update(data_fields)
        super().fix(data_mapfields)

    def normalize(self):
        self.data_pos = self.data_pos.fillna("")
        super().normalize()

    def analyze(self) -> dict[tuple[_K, ClientField], Index | MultiIndex]:
        analysis = super().analyze()
        analysis_pos = {}

        for mapfield, value in analysis.items():
            fields = self.mapfields[mapfield]
            for field in fields:
                analysis_pos[(field, mapfield)] = value
            if not fields:
                analysis_pos[(None, mapfield)] = value

        return analysis_pos

    def autofix(self, analysis: dict[tuple[_K, ClientField], Index | MultiIndex]):
        # NO autofix client data pos
        # autofix client data
        super_analysis = {mapfield: v for (_, mapfield), v in analysis.items()}
        super().autofix(super_analysis)

    def mapdata(self, mapfields: set[tuple[_K, ClientField]]):
        """Toma los datos de los campos principales y los mapea en los campos que relaciona."""
        data = {}

        for (field, mapfield) in mapfields:
            value = self.data_pos[field] if not field is None else self.data[mapfield]
            data[field, mapfield] = value

        self.fix(data)

    def fullfix(self) -> dict[tuple[_K, ClientField], Index | MultiIndex]:
        self.normalize() # crea los campos que no existen para el mapeo.
        self.mapdata(self.mapfields)
        return super().fullfix()

    def exceptions(self, analysis: dict[tuple[_K, ClientField], Index | MultiIndex]):
        analysis_mapfields = {mapfields[1]: v for mapfields, v in analysis.items()}
        return super().exceptions(analysis_mapfields)
