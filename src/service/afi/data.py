"""Modulo para gestionar los datos en cache de la intefaz contable."""

from uuid import UUID
from datetime import timedelta
from quart import has_request_context, request
from quart.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError, InternalServerError
from data.store import DataStore
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.afi import AFI, AFITransfers

DS_AFI: DataStore[AFI] = DataStore(
    max_length=7,                         # 7 sitios disponibles para crear data AFI.
    max_size=35 * 1e6,                    # 35 Megabytes.
    max_duration=timedelta(minutes=70)    # 10 minutos cada item
)

DS_AFI_TRANFERS: DataStore[AFITransfers] = DataStore(
    max_length=7,                         # 7 sitios disponibles para crear data AFI.
    max_size=35 * 1e6,                    # 35 Megabytes.
    max_duration=timedelta(minutes=70)    # 10 minutos cada item
)

def ds_afi_calc_size(afi: AFI):
    """Callback para calcular el tamaño de los datos de la interfaz contable."""
    size = int(afi.data.memory_usage(deep=True).sum())
    return size

DS_AFI.calc_size = ds_afi_calc_size
DS_AFI_TRANFERS.calc_size = ds_afi_calc_size

async def source_from_request(source: DataIO, mode: ModeDataIO):
    """Obtiene un fileio desde un contexto de request."""
    if mode == "request":
        if not has_request_context():
            raise InternalServerError("no hay contexto de un request HTTP")

        payload = "payload.files"
        if isinstance(source, str):
            payload = source

        source: FileStorage = (await request.files).get(payload)

        if not source:
            msg = "no se ha encontrado el archivo en la peticion con paylaod/key: " + payload
            raise BadRequestKeyError(msg)

    return source

async def create(*,
                 source: DataIO = None,
                 support: SupportDataIO = "csv",
                 mode: ModeDataIO = "raw",
                 dataid: UUID = None,
                 force: bool = False,
                 **kwargs: ...):
    """Crea una instancia de AFI y la guarda en un DataStore, devuelve el ID."""
    source = await source_from_request(source, mode)
    data = AFI(
        source=source,
        support=support,
        mode=mode,
        **kwargs
    )

    if not isinstance(dataid, UUID) and not dataid is None:
        raise TypeError("el parametro dataid debe ser de tipo string[UUID]")

    uuid = DS_AFI.append(data, force=force)
    if dataid:
        afi = DS_AFI.pop(uuid)
        DS_AFI[dataid] = afi
    else:
        dataid = uuid
    return dataid

async def create_transfers(*,
                           source: DataIO = None,
                           support: SupportDataIO = "csv",
                           mode: ModeDataIO = "raw",
                           dataid: UUID = None,
                           force: bool = False,
                           **kwargs: ...):
    """Crea una instancia de AFITransfers y la guarda en un DataStore, devuelve el ID."""
    source = await source_from_request(source, mode)
    data = AFITransfers(
        source=source,
        support=support,
        mode=mode,
        **kwargs
    )

    if not isinstance(dataid, UUID) and not dataid is None:
        raise TypeError("el parametro dataid debe ser de tipo string[UUID]")

    uuid = DS_AFI_TRANFERS.append(data, force=force)
    if dataid:
        afi = DS_AFI_TRANFERS.pop(uuid)
        DS_AFI_TRANFERS[dataid] = afi
    else:
        dataid = uuid
    return dataid
