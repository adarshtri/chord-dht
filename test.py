# import xmlrpc.client
# s = xmlrpc.client.ServerProxy('http://192.168.0.137:4001/RPC2')
# print(s.get_finger_table())

from client.chord_client import ChordClient
import uuid
from random import randrange

i = "localhost:4005"
i = i.strip()

# client = ChordClient(bootstrap_server="localhost:5004")
#
# keys = []
#
# f = open("/Users/atrivedi/StudyMaterial/Projects/chord-dht/sample.txt", "r")
# a = f.read()
# a = a.split(" ")

# a = list(range(99999, 10000000, 10000))
#
# for i, aa in enumerate(a):
#     if i % 100 == 0:
#         print(i)
#     print(client.set(key=aa, hash_it=False))

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


def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        yield S[(S[i] + S[j]) % 256]

def encryptRC4(plaintext, key, hexformat=False):
    key, plaintext = bytearray(key), bytearray(plaintext)  # necessary for py2, not for py3
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    keystream = PRGA(S)
    return b''.join(b"%02X" % (c ^ next(keystream)) for c in plaintext) if hexformat else bytearray(c ^ next(keystream) for c in plaintext)

print(encryptRC4(b'John Doe', b'mypass'))                           # b'\x88\xaf\xc1\x04\x8b\x98\x18\x9a'
print(encryptRC4(b'\x88\xaf\xc1\x04\x8b\x98\x18\x9a', b'mypass'))