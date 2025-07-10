"""Pruebas basicas para el servicios de los clientes"""

from service import SERVICES_GROUPS

print(SERVICES_GROUPS.info())
print(SERVICES_GROUPS)

clients_mapfields_getall = SERVICES_GROUPS["mapfields_group", "mapfields_clients", "getall"]
clients_data_fromfile = SERVICES_GROUPS["clients_group", "clients_data", "fromfile"]
clients_data_get = SERVICES_GROUPS["clients_group", "clients_data", "get"]

result_clients_mapfields_getall = clients_mapfields_getall.run({"parameters": [None, "hello"]})
uuid_mapfields = result_clients_mapfields_getall['data'][0]

print(result_clients_mapfields_getall)
# print(uuid_mapfields)

result_clients_data_fromfile = clients_data_fromfile.run({
    "parameters": []
})

uuid_clients_data: str = result_clients_data_fromfile["data"]

print(result_clients_data_fromfile)
# print(uuid_clients_data)

result_clients_data_get = clients_data_get.run({
    "parameters": [uuid_clients_data],
})
clients_data = result_clients_data_get["data"]

print(result_clients_data_get)
# print(clients_data)

print("END DEBUG")
