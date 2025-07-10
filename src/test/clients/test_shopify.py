"""Test para los clientes de CEGID Y2 Retail"""

from pathlib import Path
from pandas import concat, Series, to_datetime, Timestamp
from core.clients import ClientsShopify, MAPFIELDS_POS_SHOPIFY_MX, ClientField, ClientFieldShopifyMx

path = Path(r"C:\Users\MC\OneDrive - MAS S.A.S (1)\Documentos\INTERFAZ CONTABLE\2025-JUNIO\Clientes\Planos")
path_saved = path.parent / "Corregidos/"
path_saved.mkdir(exist_ok=True)
path_glob = path.glob("*.xlsx")
excel_file = path_saved / "Clientes_Junio_Shopify.xlsx"
data_to_concat = []

codigos_postales = ["76001", "23001", "05001"]
count = 0

key_tipo_documento = (ClientFieldShopifyMx.MF_TIPO_DE_DOCUMENTO, ClientField.TIPOIDENTIFICACION)
key_codigo_postal = (ClientFieldShopifyMx.ADDRESS_ZIP, ClientField.CODIGOPOSTAL)

for fpath in path_glob:
    clients = ClientsShopify(fpath, ftype="excel", mapfields=MAPFIELDS_POS_SHOPIFY_MX)
    analysis = clients.fullfix()

    clients.fix({
        key_tipo_documento: Series("Cédula de ciudadanía", index=analysis[key_tipo_documento]),
        key_codigo_postal: Series(codigos_postales[count], index=analysis[key_codigo_postal]),
    })

    analysis = clients.fullfix()

    # clients.data.to_csv(path_saved / fpath.name, sep="|", index=False)

    data_to_concat.append(clients.data)
    count += 1
    print(fpath.name)

df_excel = concat(data_to_concat, ignore_index=True)

df_excel = df_excel[~(df_excel[ClientField.NUMERODOCUMENTO] == "")]

# df_excel.to_excel(excel_file, index=False)

df_fecha = to_datetime(df_excel[ClientField.FECHADECREACION], format="%d/%m/%Y")

def hard_month(date: Timestamp):
    return Timestamp(year=2025, month=6, day=date.day)

df_fecha = df_fecha.apply(hard_month)

for fecha, grupo in df_excel.groupby(df_fecha.dt.date):
    fecha_f = fecha.strftime("%Y%m%d")
    file_name = f"ClientesHcos_{fecha_f}_0700_shopify.txt"
    grupo.to_csv(path_saved / file_name, sep="|", index=False)

# df_excel.to_csv(path_saved / "ClientesHcos_20241206_0700_shopify.txt", sep="|", index=False)

print("End Debug")

# Metafield: custom.tipo_de_documento [single_line_text_field]
# Metafield: custom.tipo_documento [single_line_text_field]
