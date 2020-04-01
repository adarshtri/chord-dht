import xmlrpc.client
s = xmlrpc.client.ServerProxy('http://192.168.0.137:4001/RPC2')
print(s.get_finger_table())
