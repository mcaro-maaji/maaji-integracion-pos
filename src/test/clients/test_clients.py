"""Tests basicos para la funcionalidad de los clientes."""

from core.clients import (
    ClientsCegid,
    MAPFIELDS_POS_CEGID,
    ClientsShopify,
    MAPFIELDS_POS_SHOPIFY_MX
)

clients_cegid = ClientsCegid("../test/data/examples/clients/ClientesHcos_20250302.xlsx", mapfields=MAPFIELDS_POS_CEGID, ftype="excel")
print(clients_cegid.fullfix())
clients_cegid.data.to_json("../test/data/examples/clients/ClientesHcos_20250302.json", orient="split")

# clients_shopify = ClientsShopify("../test/data/examples/clients/ClientesShopify.csv", delimiter=",", mapfields=MAPFIELDS_POS_SHOPIFY_MX)
# print(clients_shopify.fullfix())
# print(clients_shopify.fullfix())
# clients_shopify.data.to_excel("../test/data/examples/clients/Clientes_tests_output.xlsx")
