import os
import sys
from messaging.rpc import XMLRPCChordServerManager
from utilities.configuration import ConfigurationManager
from constants.configuration_constants import ConfigurationConstants


def start_chord_node():
    XMLRPCChordServerManager.start_server()


def stop_chord_node():
    XMLRPCChordServerManager.stop_server()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Kindly provide the location for configuration file.")
        exit(1)

    configuration_file = sys.argv[1]
    os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = configuration_file
    ConfigurationManager.reset_configuration()
    start_chord_node()

    while True:
        console_input = input("1. \"stop\" to shutdown chord node\n2. \"reset\" to reload new configuration\n"
                              "Enter your input:")
        if console_input.strip() == "stop":
            stop_chord_node()
            break

        if console_input.strip() == "reset":
            ConfigurationManager.reset_configuration()
