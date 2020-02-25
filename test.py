from messaging.socket_messaging import ChordSocketClient
from utilities.configuration import ConfigurationManager
from constants.configuration_constants import ConfigurationConstants
import sys
import os

if len(sys.argv) != 2:
    print("Kindly provide the location for configuration file.")
    exit(1)

configuration_file = sys.argv[1]
os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = configuration_file
ConfigurationManager.reset_configuration()

client = ChordSocketClient(host=ConfigurationManager.get_configuration().get_advertised_ip(),
                           port=ConfigurationManager.get_configuration().get_socket_port(),
                           message="Hi")
client.send()
