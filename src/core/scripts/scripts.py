"""Modulo para la lectura de los scripts."""

from pandas import Series, Index, MultiIndex
from data.io import BaseDataIO, DataIO, SupportDataIO, ModeDataIO
from utils.schedule import schedulejob_status, is_schedulejob_params
from scripts import SERVICES_GROUPS
from .fields import ScriptField
from .exceptions import (
    ScriptsException,
    ScriptsWarning,
    NoMatchScriptFieldsWarning,
    IncorrectScriptFieldsWarning,
)

class Scripts(BaseDataIO):
    """Clase para la gestion de datos de los scripts."""

    def __init__(self,
                 *,
                 source: DataIO = None,
                 destination: DataIO = None,
                 support: SupportDataIO = "object",
                 mode: ModeDataIO = "object",
                 **kwargs: ...):
        """Crea un dataframe manipulable para la informacion de los scripts."""
        super().__init__(source, destination, support, mode)

        header = kwargs.pop("header", "no defined")
        if support != "json" and header is None and "names" not in kwargs:
            kwargs["names"] = list(ScriptField)

        self.load(**kwargs)
        self.data.fillna("", inplace=True)

    def no_match_fields(self):
        """Comprueba los campos que NO existen en el DataFrame."""
        no_match_list = [i for i in ScriptField if i not in self.data]
        return set(no_match_list)

    def incorrect_fields(self):
        """Comprueba los campos que son incorrectos en el DataFrame."""
        incorrect_list = [i for i in self.data if i not in list(ScriptField)]
        return set(incorrect_list)

    def sort_fields(self, fields: list[ScriptField] = None):
        """Organiza los campos y elimina los incorrectos."""
        if not fields:
            fields = list(ScriptField)
        fields = list(dict.fromkeys(fields)) # Campos unicos y ordenados
        self.data = self.data[fields]

    def fix(self, data: dict[ScriptField, Series]):
        """Actualiza los datos segun los campos."""
        self.data.update(data)

    def analyze(self):
        """Analiza los datos y devuelve los erroes encontrados."""

        id_script = self.data[ScriptField.ID]
        id_script = id_script[id_script.duplicated()]

        name = self.data[ScriptField.NAME]
        name = name[name == ""]

        if ScriptField.DESCRIPTION in self.data:
            description = self.data[ScriptField.DESCRIPTION]
            description_index = description[description == ""].index
        else:
            description_index = self.data.index.copy()

        def is_service(value: list[str]):
            service_obj = SERVICES_GROUPS.get(*value)
            return not service_obj is None

        script = self.data[ScriptField.SCRIPT].str.split(".")
        script = script[~script.apply(is_service)]

        def is_parameters(value):
            return isinstance(value, (list, tuple))

        def is_dict(value):
            return isinstance(value, dict)

        def is_schedule(value):
            return is_schedulejob_params(value)

        parameters = self.data[ScriptField.PARAMETERS]
        parameters = parameters[~parameters.apply(is_parameters)]

        parameterskv = self.data[ScriptField.PARAMETERSKV]
        parameterskv = parameterskv[~parameterskv.apply(is_dict)]

        context = self.data[ScriptField.CONTEXT]
        context = context[~context.apply(is_dict)]

        schedule = self.data[ScriptField.SCHEDULE]
        schedule = schedule[~schedule.apply(is_schedule)]

        schedule_status = self.data[ScriptField.SCHEDULE_STATUS].astype(str)
        schedule_status = schedule_status[~schedule_status.isin(schedulejob_status)]

        return {
            ScriptField.ID: id_script.index,
            ScriptField.NAME: name.index,
            ScriptField.DESCRIPTION: description_index,
            ScriptField.SCRIPT: script.index,
            ScriptField.PARAMETERS: parameters.index,
            ScriptField.PARAMETERSKV: parameterskv.index,
            ScriptField.CONTEXT: context.index,
            ScriptField.SCHEDULE: schedule.index,
            ScriptField.SCHEDULE_STATUS: schedule_status.index
        }

    def exceptions(self, analysis: dict[ScriptField, Index | MultiIndex]):
        """Obtiene todos los errores y los mensajes propios por cada campo de los scripts."""
        no_match_fields = self.no_match_fields()
        incorrect_fields = self.incorrect_fields()
        fields_exceptions = [ScriptsException(field, list(idx))
                             for field, idx in analysis.items()
                             if field in ScriptsException and len(idx) > 0]

        fields_warnings = [ScriptsWarning(field, list(idx))
                           for field, idx in analysis.items()
                           if field in ScriptsWarning and len(idx) > 0]

        return (
            NoMatchScriptFieldsWarning(no_match_fields) if no_match_fields else None,
            IncorrectScriptFieldsWarning(incorrect_fields) if incorrect_fields else None,
            *fields_exceptions,
            *fields_warnings
        )
