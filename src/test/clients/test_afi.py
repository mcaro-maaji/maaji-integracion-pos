"""Test para la gestion de la interfaz contable."""

from pathlib import Path
from pandas import read_csv, concat, to_datetime

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-JUNIO\Planos")
path_saved = path.parent
path_saved.mkdir(exist_ok=True)
path_glob = path.glob("*.txt")
plane_file = path / "IC_20250627_20250630.txt"
data_to_concat = []

for fpath in path_glob:
    afi = read_csv(fpath, delimiter=";", header=None, dtype=str).fillna("")
    afi.astype(str)
    data_to_concat.append(afi)
    print(fpath.name)

df_excel = concat(data_to_concat, ignore_index=True)
df_excel.drop_duplicates(inplace=True)
df_excel.to_csv(plane_file, sep=";", index=False, header=None)

# df_fecha = to_datetime(df_excel[ClientField.FECHADECREACION], format="%d/%m/%Y")

# for fecha, grupo in df_excel.groupby(df_fecha.dt.date):
#     fecha_f = fecha.strftime("%Y%m%d")
#     file_name = f"ClientesHcos_{fecha_f}_0700_shopify.txt"
#     grupo.to_csv(path_saved / file_name, sep="|", index=False)

print("End Debug")
