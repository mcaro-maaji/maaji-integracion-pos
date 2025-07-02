"""Modulo para definir utilidades compartidas en todas las caracteristicas de la aplicacion."""

from typing import Literal

StatusIdIntegration = Literal["integrated", "reject", "empty"]

def check_id_integration(value: str) -> StatusIdIntegration:
    """Verifica el estado de integracion de las caracteristicas Bills, Products, Prices."""
    value = value.strip()
    if value.endswith("I"):
        return "integrated"
    if value.endswith("R"):
        return "reject"
    return "empty"

def renovate_id_integration(value: str) -> str:
    """Retira el estado de integracion del valor dejando un espacio en blanco."""
    value = value.strip()
    status = check_id_integration(value)
    if status != "empty":
        value = value[0:-1]
    return value + " "
