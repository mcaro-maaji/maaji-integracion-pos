"""Test para los clientes de CEGID Y2 Retail"""

from pathlib import Path
from pandas import concat, Series
from core.clients import ClientsCegid, MAPFIELDS_CLIENTS_POS_CEGID
from core.clients.fields import ClientField

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-JUNIO\Clientes\Planos")
path_saved = path.parent / "Corregidos/"
path_saved.mkdir(exist_ok=True)
path_glob = path.glob("*.txt")
excel_file = path / "Clientes_Junio.xlsx"
data_to_concat = []

for fpath in path_glob:
    clients = ClientsCegid(
        MAPFIELDS_CLIENTS_POS_CEGID,
        source=fpath,
        support="csv",
        mode="path",
        sep="|",
        encoding="utf-8"
    )

    analysis = clients.fullfix()

    key_codigo_postal = (ClientField.CODIGOPOSTAL, ClientField.CODIGOPOSTAL)

    clients.fix({
        key_codigo_postal: Series("05001", index=analysis[key_codigo_postal]),
    })

    clients.fullfix()

    print(fpath.name)

    clients.data.to_csv(path_saved / fpath.name, sep="|", index=False)
    # data_to_concat.append(clients.data)

# df_excel = concat(data_to_concat, ignore_index=True)
# df_excel.to_excel(excel_file)

print("End Debug")
