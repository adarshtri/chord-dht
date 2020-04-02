# import xmlrpc.client
# s = xmlrpc.client.ServerProxy('http://192.168.0.137:4001/RPC2')
# print(s.get_finger_table())

from client.chord_client import ChordClient

i = "localhost:4001"
i = i.strip()

client = ChordClient(bootstrap_server=i)

keys = []

while True:
    ip = input("get / put / del ? ")

    key = input("Enter key: ")

    if ip == "get":
        print(client.get(key))

    if ip == "put":
        print(client.store(key))

    if ip == "del":
        print(client.delete(key))
