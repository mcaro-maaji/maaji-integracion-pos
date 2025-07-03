"""Modulo para disponer de todos los recursos a la web a modo de servicio de las facturas."""

from io import BytesIO, BufferedIOBase
from quart import jsonify, send_file
import core
from service import services, common, settings, data

def get_setting(keyname: settings.params.SettingsKeyName):
    """Obtiene la configuracion especifica."""
    if keyname == "municipios":
        return settings.municipios.DANE_MUNICIPIOS
    if keyname == "stores":
        return settings.stores.STORES
    if keyname == "providers":
        return settings.providers.PROVIDERS
    if keyname == "afiparameters":
        return settings.afi_params.AFI_PARAMETERS
    raise TypeError("se debe elegir una configuracion con el nombre")

@services.operation(settings.params.keyname, settings.returns.datajson)
def get(keyname: settings.params.SettingsKeyName):
    """Obtiene los datos de las configuraciones."""
    orientjson = "records" # <- En String JSON - mejor rendimiento
    if keyname == "municipios":
        return settings.municipios.get(orientjson=orientjson)
    if keyname == "stores":
        return settings.stores.get(orientjson=orientjson)
    if keyname == "providers":
        return settings.providers.get(orientjson=orientjson)
    if keyname == "afiparameters":
        return settings.afi_params.get(orientjson=orientjson)
    raise TypeError("se debe elegir una configuracion con el nombre")

@services.operation(
    settings.params.keyname,
    common.returns.response,
    filename=common.params.filename,
    destination=data.params.destination,
    support=data.params.support,
    mode=data.params.mode,
    encoding=common.params.encoding,
    delimeter=common.params.delimeter,
    sep=common.params.sep,
    orient=common.params.orientjson,
    excel=settings.params.excel,
    index=settings.params.index,
    header=common.params.header
)
async def download(
                   keyname: settings.params.SettingsKeyName,
                   *, filename: str | None = None,
                   **kwargs: ...):
    """Descarga o copia al porpapeles la informacion de las configuraciones."""
    support = kwargs.get("support", "excel")
    destination = kwargs.pop("destination", None) or BytesIO()

    if keyname == "municipios":
        settings.municipios.save(destination=destination, **kwargs)
        default_filename = core.dane.FILENAME_DANE_MUNICIPIOS
    elif keyname == "stores":
        settings.stores.save(destination=destination, **kwargs)
        default_filename = core.stores.FILENAME_STORES
    elif keyname == "providers":
        default_filename = core.providers.FILENAME_PROVIDERS
        settings.providers.save(destination=destination, **kwargs)
    elif keyname == "afiparameters":
        default_filename = core.afi.FILENAME_AFI_PARAMETERS
        settings.afi_params.save(destination=destination, **kwargs)
    else:
        raise TypeError("se debe elegir una configuracion con el nombre")

    if support == "clipboard":
        status = 0, "la informacion se ha copiado al portapapeles"
        return jsonify(common.returns.exitstatus(status))

    if not filename:
        filename = default_filename

    if isinstance(destination, BufferedIOBase):
        destination.seek(0)

    return await send_file(destination, as_attachment=True, attachment_filename=filename)

service = services.service("settings", get, download)
