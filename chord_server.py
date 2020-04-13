import os
import sys
from messaging.rpc import XMLRPCChordServerManager
from utilities.configuration import ConfigurationManager
from constants.configuration_constants import ConfigurationConstants
from consistent_hashing import Consistent_Hashing
import sched
import time
import threading

scheduler = sched.scheduler(time.time, time.sleep)
logger = None


def stabilize_call(chord_node) -> None:
    try:
        chord_node.stabilize()
        chord_node.fix_fingers()
        #chord_node.replication_stabilization()
    except Exception as e:
        logger.exception("Something went wrong with stabilization.")
    scheduler.enter(ConfigurationManager.get_configuration().get_stabilize_interval(), 1, stabilize_call, (chord_node,))


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
    from chord.node import Node
    from utilities.app_logging import Logging
    logger = Logging.get_logger(__name__)

    server_ip = ConfigurationManager.get_configuration().get_chord_server_ip()
    server_port = ConfigurationManager.get_configuration().get_socket_port()
    server_id = Consistent_Hashing.get_modulo_hash(server_ip + ":" + str(server_port), ConfigurationManager.get_configuration().get_m_bits())
    node = Node(node_id=server_id,node_ip=server_ip, bootstrap_node=bootstrap_server)

    start_chord_node(node)
    node.join()
    scheduler.enter(ConfigurationManager.get_configuration().get_stabilize_interval(), 1, stabilize_call, (node,))
    stabilization_thread = threading.Thread(target=scheduler.run, args=(True,))
    stabilization_thread.start()

    while True:

        print("\n\nRunning with server id : " + str(server_id))
        console_input = input("1. \"stop\" to shutdown chord node\n2. \"reset\" to reload new configuration\n"
                              "3. \"pred\" Get predecessor\n4. \"succ\" Get successor\n5. \"ftable\" Finger Table\n"
                              "6. \"store\" Store\n7. \"ssize\" Store Size\n8. \"set\" Set a key\n"
                              "9. \"get\" Get a key location\n10. \"del\" Delete a key\n"
                              "Enter your input:")
        if console_input.strip() == "stop":
            while True:
                try:
                    scheduler.cancel(scheduler.queue[0])
                    stabilization_thread.join()
                    break
                except:
                    continue
            node.leave()
            stop_chord_node()
            break

        if console_input.strip() == "reset":
            ConfigurationManager.reset_configuration()

        if console_input.strip() == "pred":
            print("\nPredecessor is : {}.".format(node.get_predecessor()))

        if console_input.strip() == "succ":
            print("\nSuccessor is : {}.".format(node.get_successor()))

        if console_input.strip() == "succ_list":
            print("\nSuccessor list is : {}.".format(node.get_successor_list()))

        if console_input.strip() == "ftable":
            print(str(node.get_finger_table()))

        if console_input.strip() == "store":
            print("\nStore\n\n {}".format(node.get_store()))

        if console_input.strip() == "ssize":
            print("\nStore size for this node is {}.".format(len(node.get_store())))

        if console_input.strip() == "set":
            store_input = input("\nEnter value to be stored:")
            print("Key stored on : {}.".format(node.set(store_input.strip())))

        if console_input.strip() == "get":
            get_input = input("\nEnter value to be retrieved:")
            print("Key is on : {}.".format(node.get(get_input.strip())))

        if console_input.strip() == "del":
            del_input = input("\nEnter value to be deleted:")
            print("Key deleted on : {}.".format(node.delete(del_input.strip())))
