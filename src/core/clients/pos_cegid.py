"""Modulo para organizar la inforamcion de los clientes segun el Sistema POS de CEGID Y2 Retail."""

from core.mapfields import MapFields
from .pos import ClientsPOS
from .fields import ClientField

class ClientsCegid(ClientsPOS[ClientField]):
    """Clientes que se manejan segun el pos de CEGID RETAIL Y2."""

MAPFIELDS_POS_CEGID = MapFields(*zip(ClientField, ClientField))
