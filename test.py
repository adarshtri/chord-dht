# import xmlrpc.client
# s = xmlrpc.client.ServerProxy('http://192.168.0.137:4001/RPC2')
# print(s.get_finger_table())

from client.chord_client import ChordClient
import uuid
from random import randrange

i = "localhost:4005"
i = i.strip()

# client = ChordClient(bootstrap_server="152.7.99.157:4000")
#
# keys = []
#
# f = open("/Users/atrivedi/StudyMaterial/Projects/chord-dht/sample.txt", "r")
# a = f.read()
# a = a.split(" ")
#
# for i, aa in enumerate(a):
#     if i % 100 == 0:
#         print(i)
#     print(client.get(aa))

# while True:
#     ip = input("get / put / del ? ")
#
#     key = input("Enter key: ")
#
#     if ip == "get":
#         print(client.get(key))
#
#     if ip == "put":
#         print(client.store(key))
#
#     if ip == "del":
#         print(client.delete(key))

import random
print(random.randint(0, 1))
