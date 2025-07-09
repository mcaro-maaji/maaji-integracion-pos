"""Modulo de scripts para datos de los clientes con el pos cegid."""

from datetime import datetime
from io import IOBase, StringIO
from app.logging import get_logger
from core.clients import ClientsCegid, MAPFIELDS_CLIENTS_POS_CEGID
from service import services, common
from scripts import cegid

logger = get_logger("auto", "scripts.cegid.clients")

@services.operation(common.returns.exitstatus, context=cegid.params.context)
def fullfix(*, context: dict):
    """Repara los archivos de los clientes."""
    context_files_to_input = context.get("files_to_input") or []
    context_download_files = context.get("download_files") or []
    context_files = []
    context_upload_files = []

    for file_local, file_source in zip(context_files_to_input, context_download_files):
        if not isinstance(file_source, IOBase):
            raise TypeError("el archivo debe ser un buffer")

        file_destination = StringIO()

        clients = ClientsCegid(
            MAPFIELDS_CLIENTS_POS_CEGID,
            source=file_source,
            destination=file_destination,
            support="csv",
            mode="buffer",
            sep="|"
        )

        file_destination.seek(0)
        clients.fullfix()
        clients.save("csv", "buffer", fixed=True, sep="|", index=False)
        file_destination.seek(0)
        context_files.append(file_local)
        context_upload_files.append(file_destination)
        logger.info("se ha reparado el archivo de clientes '%s'", file_local)

    context["files"] = context_files
    context["upload_files"] = context_upload_files

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    patter_by_input=cegid.params.patter,
    patter_by_procesa=cegid.params.patter,
    patter_by_error=cegid.params.patter,
    dirpath_input=common.params.raw,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def integratedata(*,
                  context: dict,
                  patter: str,
                  patter_by_input: str,
                  patter_by_procesa: str,
                  patter_by_error: str,
                  dirpath_input: str,
                  after_at: datetime = None,
                  before_at: datetime = None):
    """Integra los archivos de los clientes."""
    context["integration_state"] = "out"
    cegid.operations.getfiles(patter, context, after_at, before_at)
    context["integration_state"] = "input"
    cegid.operations.getfiles(patter_by_input, context, after_at, before_at)
    context["integration_state"] = "procesa"
    cegid.operations.getfiles(patter_by_procesa, context, after_at, before_at)
    context["integration_state"] = "error"
    cegid.operations.getfiles(patter_by_error, context, after_at, before_at)

    cegid.operations.flowintegration(context=context)
    cegid.operations.dirpathinput(dirpath_input, context=context)
    cegid.operations.downloadfiles(context)
    fullfix(context=context)

    if not context.get("test"):
        cegid.operations.uploadfiles(context)

    context_files = len(context.get("files") or [])
    logger.info("se han integrado %d archivos de clientes con exito", context_files)

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    patter_by_input=cegid.params.patter,
    patter_by_procesa=cegid.params.patter,
    patter_by_error=cegid.params.patter,
    dirpath_input=common.params.raw,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def test(*,
         context: dict,
         patter: str,
         patter_by_input: str,
         patter_by_procesa: str,
         patter_by_error: str,
         dirpath_input: str,
         after_at: datetime = None,
         before_at: datetime = None):
    """Prueba para integrar los archivos de los clientes sin subirlos al FTP"""
    context["test"] = True

    integratedata(
        context=context,
        patter=patter,
        patter_by_input=patter_by_input,
        patter_by_procesa=patter_by_procesa,
        patter_by_error=patter_by_error,
        dirpath_input=dirpath_input,
        after_at=after_at,
        before_at=before_at
    )

    context["test"] = False

service = services.service("clients", fullfix, integratedata, test)
