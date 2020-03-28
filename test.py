import xmlrpc.client
s = xmlrpc.client.ServerProxy('http://localhost:4003/RPC2')
print(s.get_finger_table())
