"""Modulo de scripts para datos de la interfaz contable con el pos cegid."""

from datetime import datetime, timedelta
from io import StringIO
from pandas import concat as pandas_concat, to_datetime as pandas_to_datetime
from app.logging import get_logger
from core.afi import AFI, AFITransfers
from core.afi.fields import AFIField
from service import services, common
from scripts import cegid

logger = get_logger("auto", "scripts.cegid.afi")

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def get_afi_transfers(*,
                      context: dict,
                      patter: str,
                      after_at: datetime = None,
                      before_at: datetime = None):
    """
    Busca y descarga los archivos de las transferencias y agrupa en una instancia AFITransfers.
    """
    context["integration_state"] = "out"
    cegid.operations.getfiles(patter, context, after_at, before_at)
    context["files"] = context.get("files_by_out")
    cegid.operations.downloadfiles(context)

    context_files_transfers_support = context.get("files_transfers_support") or "csv"
    context_files_transfers_header = context.get("files_transfers_header") or None
    context_files_transfers_sep = context.get("files_transfers_sep") or ";"
    context_download_files = context.get("download_files") or []
    all_afi_transfers: list[AFITransfers] = []

    for file_source in context_download_files:
        try:
            afi_transfers = AFITransfers(
                source=file_source,
                support=context_files_transfers_support,
                mode="buffer",
                index=False,
                header=context_files_transfers_header,
                sep=context_files_transfers_sep
            )
            all_afi_transfers.append(afi_transfers)
        except Exception:
            continue

    df_afi_transfers = pandas_concat([afi_t.data for afi_t in all_afi_transfers], ignore_index=True)
    afi_tranfers = AFITransfers(source=df_afi_transfers)
    context["afi_transfers"] = afi_tranfers
    context["files"] = []

def _get_afi_files(*, context: dict):
    """Descarga los archivos y los agrupa en una instancia AFI."""
    context_download_files = context.get("download_files") or []
    all_afi_files: list[AFI] = []

    for file_source in context_download_files:
        try:
            afi_file = AFI(
                source=file_source,
                support="csv",
                mode="buffer",
                sep=";",
                index_col=False,
                header=None
            )
            all_afi_files.append(afi_file)
        except Exception:
            continue

    try:
        df_afi_files = pandas_concat([afi.data for afi in all_afi_files], ignore_index=True)
        afi_files = AFI(source=df_afi_files)
    except Exception:
        afi_files = None

    context["afi_files"] = afi_files
    context["files"] = []

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def get_afi_duplicates(*,
                      context: dict,
                      patter: str,
                      after_at: datetime = None,
                      before_at: datetime = None):
    """
    Busca los archivos de con posibilidad de duplicados en la carpeta procesa de interfaz contable.
    """
    context["integration_state"] = "procesa"
    cegid.operations.getfiles(patter, context, after_at, before_at)
    context["files"] = context.get("files_by_procesa")
    cegid.operations.downloadfiles(context)

    _get_afi_files(context=context)
    context["afi_duplicates"] = context["afi_files"]
    context["afi_files"] = []

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def get_afi_files(*,
                  context: dict,
                  patter: str,
                  after_at: datetime = None,
                  before_at: datetime = None):
    """Busca los archivos de en la carpeta por fuera de los planos de interfaz contable."""
    context["integration_state"] = "out"
    cegid.operations.getfiles(patter, context, after_at, before_at)
    context["files"] = context.get("files_by_out")
    cegid.operations.downloadfiles(context)
    _get_afi_files(context=context)

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    after_at=cegid.params.after_at,
    before_at=cegid.params.before_at
)
def fullfix(*, context: dict, after_at: datetime = None, before_at: datetime = None):
    """Repara los archivos de la interfaz contable."""
    if before_at is None:
        before_at = datetime.now()

    if after_at is None:
        after_at = before_at - timedelta(days=1)

    context_files_preffix = str(context.get("files_preffix") or "AIC")
    context_afi_files: AFI = context.get("afi_files") or None
    context_afi_transfers: AFITransfers = context.get("afi_transfers") or None
    context_afi_duplicates: AFI = context.get("afi_duplicates") or None

    context_files = []
    context_upload_files = []

    if context_afi_files:
        with open("../test/data/examples/afi/AutoIC_Test_data_antes.xlsx", "wb") as file:
            context_afi_files.data.to_excel(file, index=False)

        if context_afi_duplicates:
            with open("../test/data/examples/afi/AutoIC_Test_data_duplicados_antes.xlsx", "wb") as file:
                context_afi_duplicates.data.to_excel(file, index=False)

        context_afi_files.fullfix(context_afi_transfers, context_afi_duplicates)
        afi_fecha = context_afi_files.data[AFIField.FECHA_ELABORACION]
        afi_fecha = pandas_to_datetime(afi_fecha, format="%Y/%m/%d")

        with open("../test/data/examples/afi/AutoIC_Test_data.xlsx", "wb") as file:
            context_afi_files.data.to_excel(file, index=False)

        if context_afi_duplicates:
            with open("../test/data/examples/afi/AutoIC_Test_data_duplicados.xlsx", "wb") as file:
                context_afi_duplicates.data.to_excel(file, index=False)

        for date, afi_file in context_afi_files.data.groupby(afi_fecha.dt.date):
            if date < after_at.date() or date > before_at.date():
                continue
            datefile = date.strftime("%Y%m%d")
            timefile = datetime.now().strftime("%H%M%S")
            filename = f"{context_files_preffix}_{datefile}{timefile}.xlsx"
            buffer = StringIO()
            afi_file.to_csv(buffer, sep=";", index=False, header=False)
            context_files.append(filename)
            context_upload_files.append(buffer)
            with open("../test/data/examples/afi/" + filename, "wb") as file:
                afi_file.to_excel(file, index=False)
            logger.info("se ha reparado el archivo de interfaz contable '%s'", filename)

    context["files"] = context_files
    context["upload_files"] = context_upload_files

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    patter_by_transfers=cegid.params.patter,
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
                  patter_by_transfers: str = None,
                  after_at: datetime = None,
                  before_at: datetime = None):
    """Integra los archivos de la interfaz contable."""

    context["integration_state"] = "input"
    cegid.operations.getfiles(patter_by_input, context, after_at, before_at)

    context["integration_state"] = "error"
    cegid.operations.getfiles(patter_by_error, context, after_at, before_at)

    if patter_by_transfers:
        get_afi_transfers(
            context=context,
            patter=patter_by_transfers,
            after_at=after_at,
            before_at=before_at
        )

    get_afi_duplicates(
        context=context,
        patter=patter_by_procesa,
        after_at=after_at,
        before_at=before_at
    )

    get_afi_files(context=context, patter=patter, after_at=after_at, before_at=before_at)

    fullfix(context=context, after_at=after_at, before_at=before_at)

    cegid.operations.flowintegration(context=context)
    cegid.operations.dirpathinput(dirpath_input, context=context)

    if not context.get("test"):
        cegid.operations.uploadfiles(context)

    context_files = len(context.get("files") or [])
    logger.info("se han integrado %d archivos de IC con exito", context_files)

@services.operation(
    common.returns.exitstatus,
    context=cegid.params.context,
    patter=cegid.params.patter,
    patter_by_transfers=cegid.params.patter,
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
         patter_by_transfers: str = None,
         after_at: datetime = None,
         before_at: datetime = None):
    """Prueba para integrar los archivos de la interfaz contable sin subirlos al FTP"""
    context["test"] = True

    integratedata(
        context=context,
        patter=patter,
        patter_by_transfers=patter_by_transfers,
        patter_by_input=patter_by_input,
        patter_by_procesa=patter_by_procesa,
        patter_by_error=patter_by_error,
        dirpath_input=dirpath_input,
        after_at=after_at,
        before_at=before_at
    )

    context["test"] = False

service = services.service("afi", get_afi_transfers, get_afi_duplicates, get_afi_files,
                           fullfix, integratedata, test)
