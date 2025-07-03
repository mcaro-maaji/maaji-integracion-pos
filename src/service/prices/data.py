"""Modulo para gestionar los datos en cache de los precios de venta."""

import json
from uuid import UUID
from datetime import timedelta, datetime
from quart import has_request_context, request
from quart.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError, InternalServerError
from pandas import DataFrame
from data.store import DataStore
from data.io import DataIO, SupportDataIO, ModeDataIO
from core.prices import Prices
from providers.microsoft.api.dynamics import DynamicsApi, DynamicsKeyEnv

DS_PRICES: DataStore[Prices] = DataStore(
    max_length=7,                         # 7 sitios disponibles para crear data prices.
    max_size=35 * 1e6,                    # 35 Megabytes.
    max_duration=timedelta(minutes=70)    # 10 minutos cada item
)

def ds_prices_calc_size(prices: Prices):
    """Callback para calcular el tamaño de los datos de los precios de venta."""
    size = int(prices.data.memory_usage(deep=True).sum())
    return size

DS_PRICES.calc_size = ds_prices_calc_size

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
    """Crea una instancia de Prices y la guarda en un DataStore, devuelve el ID."""
    source = await source_from_request(source, mode)
    data = Prices(
        source=source,
        support=support,
        mode=mode,
        **kwargs
    )

    if not isinstance(dataid, UUID) and not dataid is None:
        raise TypeError("el parametro dataid debe ser de tipo string[UUID]")

    uuid = DS_PRICES.append(data, force=force)
    if dataid:
        prices = DS_PRICES.pop(uuid)
        DS_PRICES[dataid] = prices
    else:
        dataid = uuid
    return dataid

async def create_fromapi(*,
                         dynamics_env: DynamicsKeyEnv = "PROD",
                         date_end: datetime = None,
                         date_start: datetime = None,
                         data_area_id: str = None,
                         dataid: UUID = None,
                         force: bool = False,
                         **kwargs: ...):
    """Crea la instancia de Prices mediante las api de Dynamics 365."""
    if dynamics_env is None:
        dynamics_env = "PROD"
    dynamics_api = DynamicsApi.fromenv(dynamics_env, "PRICES:CEGID")
    data = dynamics_api.getdata(
        data_area_id=data_area_id,
        date_end=date_end,
        date_start=date_start
    )
    df_data = DataFrame(json.loads(data))

    return await create(
        source=df_data,
        support="object",
        mode="object",
        dataid=dataid,
        force=force,
        **kwargs
    )
