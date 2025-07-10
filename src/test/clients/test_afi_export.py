"""Test para la gestion de la interfaz contable."""

from pathlib import Path
from pandas import read_csv, concat, to_datetime

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-JUNIO")
path_glob = path.glob("*.csv")
data_to_concat = []

for fpath in path_glob:
    afi = read_csv(fpath, delimiter=";", header=None, dtype=str).fillna("")
    afi.astype(str)
    data_to_concat.append(afi)
    print(fpath.name)

df_afi = concat(data_to_concat, ignore_index=True)
df_afi_fecha = to_datetime(df_afi[5], format="%Y/%m/%d")

for fecha, grupo in df_afi.groupby(df_afi_fecha.dt.date):
    fecha_f = fecha.strftime("%Y%m%d")
    file_name = f"IC_{fecha_f}113000.txt"
    grupo.to_csv(path / file_name, sep=";", index=False, header=None)
    print(file_name)

print("End Debug")
