"""Modulo para manejar las operaciones comunes de los scripts en cegid y2 retail."""

from typing import Literal
from pathlib import Path
from io import StringIO
from datetime import datetime
from app.logging import get_logger
from service import services, common
from scripts import cegid
from .utils import get_maaji_ftp

logger = get_logger("auto", "scripts.cegid")
ContextIntegrationState = Literal["out", "input", "procesa", "error"]
list_context_integration_state: list[ContextIntegrationState] = ["out", "input", "procesa", "error"]

@services.operation(
    cegid.params.patter,
    common.returns.exitstatus,
    context=cegid.params.context,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def getfiles(patter: str, context: dict, after_at: datetime = None, before_at: datetime = None):
    """Busca los archivos en el FTP de Maaji."""
    ftp_name = context.get("ftp_name")
    ftp_host = context.get("ftp_host")
    ftp = get_maaji_ftp(ftp_name, ftp_host)
    list_files = ftp.list_files_by_date(patter, after_at, before_at)
    context_integration_state = context.get("integration_state") or "out"

    if context_integration_state not in list_context_integration_state:
        context_integration_state = "out"

    key_files_by = f"files_by_{context_integration_state}"
    context[key_files_by] = list_files
    return 0, f"se han encontrado un total de {len(list_files)} archivos"

@services.operation(common.returns.exitstatus, context=cegid.params.context)
def flowintegration(*, context: dict):
    """Filtra los archivos que cumplen con el flujo de la integracion en cegid y2."""
    context_files_by_out = context.get("files_by_out") or []
    context_files_by_input = context.get("files_by_input") or []
    context_files_by_procesa = context.get("files_by_procesa") or []
    context_files_by_error = context.get("files_by_error") or []

    context_files_by_input = [Path(file).name for file in context_files_by_input]
    context_files_by_procesa = [Path(file).name for file in context_files_by_procesa]
    context_files_by_error = [Path(file).name for file in context_files_by_error]

    context_download_files = []

    for file_out in context_files_by_out:
        filename_out = Path(file_out).name
        file_input = filename_out in context_files_by_input
        file_precesa = filename_out in context_files_by_procesa
        file_error = filename_out in context_files_by_error

        if not file_input and not file_precesa and not file_error:
            context_download_files.append(file_out)

    context["files"] = context_download_files
    context["files_by_out"] = []
    context["files_by_input"] = []
    context["files_by_procesa"] = []
    context["files_by_error"] = []

@services.operation(
    common.params.raw,
    common.returns.exitstatus,
    context=cegid.params.context
)
def dirpathinput(dirpath_input: str, *, context: dict):
    """Crea la ruta de archivos que cumplen con el flujo de la integracion en cegid y2."""
    context_files = context.get("files") or []
    context_files_to_input = []

    for file in context_files:
        file_to_procesa = dirpath_input + Path(file).name
        context_files_to_input.append(file_to_procesa)

    context["files_to_input"] = context_files_to_input

@services.operation(common.returns.exitstatus, context=cegid.params.context)
def downloadfiles(context: dict):
    """Descargar los archivos a una ruta especifica en el FTP Maaji"""
    ftp_name = context.get("ftp_name")
    ftp_host = context.get("ftp_host")
    ftp = get_maaji_ftp(ftp_name, ftp_host)

    context_files = context.get("files") or []
    context_download_files = []

    if not isinstance(context_files, (list, tuple)):
        raise FileNotFoundError("no hay archivos para descargar")

    for remote_file in context_files:
        if not isinstance(remote_file, str):
            raise TypeError("el valor no es una ruta de un archivo en el ftp.")

        buffer = StringIO()
        ftp.download(remote_file, buffer)
        context_download_files.append(buffer)

    context["download_files"] = context_download_files
    count_download_files = len(context_download_files)
    logger.info("se han descargado %d archivos desde FTP '%s'", count_download_files, ftp.host)
    return 0, f"se han descargado un total de {count_download_files} archivos"

@services.operation(common.returns.exitstatus, context=cegid.params.context)
def uploadfiles(context: dict):
    """Subir los archivos a una ruta especifica en el FTP Maaji"""
    ftp_name = context.get("ftp_name")
    ftp_host = context.get("ftp_host")
    ftp = get_maaji_ftp(ftp_name, ftp_host)

    context_files = context.get("files") or []
    context_upload_files = context.get("upload_files") or []

    if not isinstance(context_upload_files, (list, tuple)):
        raise FileNotFoundError("no hay archivos para subir")

    for remote_file, buffer in zip(context_files, context_upload_files):
        if not isinstance(remote_file, str):
            raise TypeError("el valor no es una ruta de un archivo en el ftp.")

        # ftp.upload(buffer, remote_file)
        with open("../test/data/examples/data_clients/" + Path(remote_file).name, "w", encoding="utf-8") as file:
            file.writelines(buffer.readlines())

    count_upload_files = len(context_files)
    logger.info("se han subido %d archivos desde FTP '%s'", count_upload_files, ftp.host)
    return 0, f"se han subido un total de {count_upload_files} archivos"

service = services.service("common", getfiles, flowintegration, dirpathinput,
                           downloadfiles, uploadfiles)
