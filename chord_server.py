import os
import sys
from messaging.rpc import XMLRPCChordServerManager
from utilities.configuration import ConfigurationManager
from constants.configuration_constants import ConfigurationConstants
from chord.node import Node
from consistent_hashing import Consistent_Hashing


def start_chord_node(chord_node):
    XMLRPCChordServerManager.start_server(chord_node)


def stop_chord_node():
    XMLRPCChordServerManager.stop_server()


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Kindly provide the location for configuration file.")
        exit(1)

    configuration_file = None
    bootstrap_server = None
    server_ip = None

    if len(sys.argv) == 2:
        configuration_file = sys.argv[1]
        bootstrap_server = None
    elif len(sys.argv) == 3:
        configuration_file = sys.argv[1]
        bootstrap_server = sys.argv[2]

    os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = configuration_file
    ConfigurationManager.reset_configuration()

    server_ip = ConfigurationManager.get_configuration().get_chord_server_ip()
    server_port = ConfigurationManager.get_configuration().get_socket_port()
    server_id = Consistent_Hashing.get_modulo_hash(server_ip + ":" + str(server_port), ConfigurationManager.get_configuration().get_m_bits())
    node = Node(node_id=server_id,node_ip=server_ip, bootstrap_node=bootstrap_server)

    start_chord_node(node)
    node.join()

    while True:
        print("\n\nRunning with server id : " + str(server_id))
        console_input = input("1. \"stop\" to shutdown chord node\n2. \"reset\" to reload new configuration\n"
                              "3. \"pred\" Get predecessor\n4. \"succ\" Get successor\n5. \"ftable\" Finger Table\n"
                              "6. \"store\" Store\n"
                              "Enter your input:")
        if console_input.strip() == "stop":
            node.leave()
            stop_chord_node()
            break

        if console_input.strip() == "reset":
            ConfigurationManager.reset_configuration()

        if console_input.strip() == "pred":
            print(node.get_predecessor())

        if console_input.strip() == "succ":
            print(node.get_successor())

        if console_input.strip() == "ftable":
            print(str(node.get_finger_table()))

        if console_input.strip() == "store":
            print(node.get_store())
