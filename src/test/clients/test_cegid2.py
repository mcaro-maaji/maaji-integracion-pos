"""Test para los clientes de CEGID Y2 Retail"""

from pathlib import Path
from pandas import concat, Series
from pandas.errors import EmptyDataError
from core.clients import ClientsCegid, MAPFIELDS_POS_CEGID, ClientField

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-MAYO\Clientes\Planos")
path_saved = path.parent
path_glob = path.glob("*.txt")
excel_file = path_saved / "Clientes_POS_20230901_20250430.xlsx"
data_to_concat = []

for fpath in path_glob:
    try:
        clients = ClientsCegid(fpath, mapfields=MAPFIELDS_POS_CEGID)
    except EmptyDataError:
        continue
    analysis = clients.fullfix()

    key_codigo_postal = (ClientField.CODIGOPOSTAL, ClientField.CODIGOPOSTAL)

    # clients.fix({
    #     key_codigo_postal: Series("05001", index=analysis[key_codigo_postal]),
    # })

    clients.fullfix()

    # clients.data.to_csv(path_saved / fpath.name, sep="|", index=False)

    data_to_concat.append(clients.data_pos)

print("concat")
df_excel = concat(data_to_concat, ignore_index=True)
df_excel.to_csv(excel_file, sep="|")

print("End Debug")
