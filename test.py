# from messaging.socket_messaging import ChordSocketClient
# from utilities.configuration import ConfigurationManager
# from constants.configuration_constants import ConfigurationConstants
# import sys
# import os
#
# if len(sys.argv) != 2:
#     print("Kindly provide the location for configuration file.")
#     exit(1)
#
# configuration_file = sys.argv[1]
# os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = configuration_file
# ConfigurationManager.reset_configuration()
#
# client = ChordSocketClient(host=ConfigurationManager.get_configuration().get_advertised_ip(),
#                            port=ConfigurationManager.get_configuration().get_socket_port(),
#                            message="Hi")
# client.send()


import xmlrpc.client

s = xmlrpc.client.ServerProxy('http://localhost:4001/RPC2')
# print(s.pow(2,3))  # Returns 2**3 = 8
# print(s.add(2,3))  # Returns 5
# print(s.mul(5,2))  # Returns 5*2 = 10

# Print list of available methods
print(s.add(1, 2))

