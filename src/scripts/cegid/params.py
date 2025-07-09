"""Modulo para definir los parametros de las operaciones en los scripts cegid y2."""

from service import services, common

@services.parameter(type="JSON")
def context(value: dict):
    """Parametro que define el contexto para las operaciones de los scripts cegid y2."""
    if not isinstance(value, dict):
        raise TypeError("el valor debe ser de tipo JSON.")
    return value

@services.parameter(type="StringLike[GlobExpression]")
def patter(value: str):
    """Parametro que define el patron para buscar archivos."""
    return common.params.raw(value)

@services.parameter(type="DateTime")
def after_at(value: str):
    """
    Parametro que define un filtro de la fecha de modificacion para buscar archivos, despuse de.
    """
    return common.params.datetimefromdelta(value)

@services.parameter(type="DateTime")
def before_at(value: str):
    """
    Parametro que define un filtro de la fecha de modificacion para buscar archivos, antes de.
    """
    return common.params.datetimefromdelta(value)
