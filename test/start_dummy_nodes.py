"""
Author: Adarsh Trivedi

This module is useful in starting dummy nodes during test runs in package test/.

Usage: python3.7 start_dummy_nodes.py [dummy_config_file_name] [node1 id] [node2 id] [node3 id] [node4 id] [node5 id]
Example: python3.7 start_dummy_nodes.py config.test.json 100000 200000 300000 400000 500000

******NOTE*****
This module doesn't handle parameter missing or invalid parameters exception. So, kindly use the specified usage
correctly to start the dummy nodes.
***************
"""


import sys
import os
from constants.configuration_constants import ConfigurationConstants
from messaging.rpc import XMLRPCChordServerManagerTest
from utilities.configuration import ConfigurationManager
import time
import threading
import sched
import json
import unittest

os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = "config.test.json"
fp = open(os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE], "w")
fp.write(json.dumps({
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5001,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord1/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": None
        }))
fp.close()
from chord.node import Node
TestNode = Node


def stabilize_call(chord_node, schedule) -> None:
    try:
        chord_node.stabilize()
        chord_node.fix_fingers()
        #chord_node.replication_stabilization()
    except Exception as e:
        print(e)
    schedule.enter(ConfigurationManager.get_configuration().get_stabilize_interval(), 1, stabilize_call, (chord_node,schedule,))


class DummyNodeManager(object):

    def __init__(self, node_ids: list):
        if len(node_ids) != 5:
            print("{} needs 5 dummy node ids to start.".format(__name__))
            exit(1)
        self.scheduler = []
        for i in range(5):
            s = sched.scheduler(time.time, time.sleep)
            self.scheduler.append(s)
        self.stabilization_thread = [None] * 5
        self._node_ids = node_ids
        self._config_file = os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE]
        self._nodes = [None]*5
        self._state = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False
        }
        self._config = [{
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5001,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord1/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": None
        },{
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5002,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord2/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": "localhost:5001"
        },{
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5003,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord3/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": "localhost:5001"
        },{
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5004,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord4/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": "localhost:5001"
        },{
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5005,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord5/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": "localhost:5001"
        }]

    @staticmethod
    def start_chord_node(chord_node, i):

        XMLRPCChordServerManagerTest.start_server(chord_node, i)

    @staticmethod
    def stop_chord_node(i):
        XMLRPCChordServerManagerTest.stop_server(i)

    def start_specific_node(self, i):

        if self._state[i]:
            print("Dummy node already running.")
        else:

            fp = open(self._config_file, 'w')
            fp.write(json.dumps(self._config[i]))
            fp.close()

            ConfigurationManager.reset_configuration()

            server_ip = self._config[i]["ip"]
            server_port = self._config[i]["socket_port"]
            server_id = self._node_ids[i]
            bootstrap_server = self._config[i]["bootstrap_server"]

            self._nodes[i] = TestNode(node_id=server_id, node_ip=server_ip, bootstrap_node=bootstrap_server)

            self.start_chord_node(self._nodes[i], i)
            self._nodes[i].join()
            self.scheduler[i].enter(ConfigurationManager.get_configuration().get_stabilize_interval(), 1,
                                    stabilize_call,
                                    (self._nodes[i], self.scheduler[i],))
            self.stabilization_thread[i] = threading.Thread(target=self.scheduler[i].run, args=(True,))
            self.stabilization_thread[i].start()
            print("Started node {}.".format(i + 1))
            self._state[i] = True
            time.sleep(3)

    def start_nodes(self):

        for i in range(len(self._config)):

            fp = open(self._config_file, 'w')
            fp.write(json.dumps(self._config[i]))
            fp.close()

            ConfigurationManager.reset_configuration()

            server_ip = self._config[i]["ip"]
            server_port = self._config[i]["socket_port"]
            server_id = self._node_ids[i]
            bootstrap_server = self._config[i]["bootstrap_server"]

            self._nodes[i] = TestNode(node_id=server_id, node_ip=server_ip, bootstrap_node=bootstrap_server)

            self.start_chord_node(self._nodes[i],i)
            self._nodes[i].join()
            self.scheduler[i].enter(ConfigurationManager.get_configuration().get_stabilize_interval(), 1, stabilize_call,
                            (self._nodes[i],self.scheduler[i],))
            self.stabilization_thread[i] = threading.Thread(target=self.scheduler[i].run, args=(True,))
            self.stabilization_thread[i].start()
            print("Started node {}.".format(i+1))
            self._state[i] = True
            time.sleep(3)

    def stop_specific_node(self, i):

        if self._state[i]:
            while True:
                try:
                    while self.scheduler[i].queue:
                        self.scheduler[i].cancel(self.scheduler[i].queue[0])
                        self.scheduler[i].queue = self.scheduler[i].queue[1:]
                    self.stabilization_thread[i].join()
                    break
                except Exception as e:
                    print("Retrying to stop node {}.".format(i+1))
                    continue
            self._nodes[i].leave()
            self.stop_chord_node(i)
            print("Stopped dummy node {}.".format(i+1))
            self._state[i] = False
        else:
            print("Dummy node already stopped.")

    def stop_specific_node_without_leave(self, i):

        if self._state[i]:
            while True:
                try:
                    while self.scheduler[i].queue:
                        self.scheduler[i].cancel(self.scheduler[i].queue[0])
                        self.scheduler[i].queue = self.scheduler[i].queue[1:]
                    self.stabilization_thread[i].join()
                    break
                except Exception as e:
                    print("Retrying to stop node {}.".format(i+1))
                    continue
            #self._nodes[i].leave()
            self.stop_chord_node(i)
            print("Stopped dummy node {}.".format(i+1))
            self._state[i] = False
        else:
            print("Dummy node already stopped.")

    def stop_all_nodes(self):
        for i in range(len(self._node_ids)-1, -1, -1):
            self.stop_specific_node(i)
            print("Stopped server {}.".format(i+1))
            self._state[i] = False


def main():

    dummy_config_file = sys.argv[1]
    os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE] = dummy_config_file
    fp = open(dummy_config_file, "w")
    fp.write(json.dumps({
            "ip": "localhost",
            "advertised_ip": "",
            "socket_port": 5001,
            "m_bits": 20,
            "stabilize_interval": 2,
            "log_file": "logs/chord1/chord.log",
            "log_to_console": 0,
            "log_frequency_interval": 5,
            "log_frequency_unit": "m",
            "log_frequency_backup_count": 10000,
            "bootstrap_server": None
        }))
    fp.close()
    from chord.node import Node
    global TestNode
    TestNode = Node
    nodes = list()
    nodes.append(int(sys.argv[2]))
    nodes.append(int(sys.argv[3]))
    nodes.append(int(sys.argv[4]))
    nodes.append(int(sys.argv[5]))
    nodes.append(int(sys.argv[6]))

    dummy_manager = DummyNodeManager(nodes)
    dummy_manager.start_nodes()

    while True:
        user_input = input("1.\"stop\" to stop dummy servers\n2.\"stop_i\" to stop ith node\n"
                           "3.\"node_i_id\" Get ith node's id\n4.\"start_i\" to start ith node\n"
                           "5.\"crash_i\" Crash i node\nEnter input:")

        if user_input.strip() == "stop":
            dummy_manager.stop_all_nodes()
            break

        elif user_input.strip() == "stop_i":
            i = None
            try:
                i = int(input("Enter i value:"))
            except:
                print("Make sure value entered is integer.")
                continue

            if i >=1 and i <=5:
                dummy_manager.stop_specific_node(i-1)
            else:
                print("We only have 5 dummy nodes. i value provided too small or too large.")

        elif user_input.strip() == "node_i_id":
            i = None
            try:
                i = int(input("Enter i value:"))
            except:
                print("Make sure value entered is integer.")
                continue

            if i >= 1 and i <= 5:
                print(dummy_manager._nodes[i-1].get_node_id(), dummy_manager._nodes[i-1].get_connection_string())
            else:
                print("We only have 5 dummy nodes. i value provided too small or too large.")

        elif user_input.strip() == "start_i":
            i = None
            try:
                i = int(input("Enter i value:"))
            except:
                print("Make sure value entered is integer.")
                continue

            if i >= 1 and i <= 5:
                try:
                    dummy_manager.start_specific_node(i-1)
                except:
                    print("Failed to start. Retry.")
                    continue
            else:
                print("We only have 5 dummy nodes. i value provided too small or too large.")

        elif user_input.strip() == "crash_i":
            i = None
            try:
                i = int(input("Enter i value:"))
            except:
                print("Make sure value entered is integer.")
                continue

            if i >= 1 and i <= 5:
                dummy_manager.stop_specific_node_without_leave(i-1)
            else:
                print("We only have 5 dummy nodes. i value provided too small or too large.")


class ChordTest(unittest.TestCase):

    def test_join(self):
        pass


if __name__ == "__main__":
    main()
