import unittest
import xmlrpc.client
import os
from constants.configuration_constants import ConfigurationConstants
import time
import json
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
from test.start_dummy_nodes import DummyNodeManager


def generate_xmlrpc_client(connection_string):
    return xmlrpc.client.ServerProxy("http://" + connection_string + "/RPC2")


class TestSuccessorsAutomated(unittest.TestCase):

    _dummy_manager = None
    id_ip_map = {
        100000: "localhost:5001",
        300000: "localhost:5002",
        500000: "localhost:5003",
        700000: "localhost:5004",
        900000: "localhost:5005"
    }

    @classmethod
    def setUpClass(cls) -> None:
        print("Initializing dummy chord nodes with ids 100000, 300000, 500000, 700000, 900000.")
        cls._dummy_manager = DummyNodeManager(node_ids=[100000, 300000, 500000, 700000, 900000])
        cls._dummy_manager.start_nodes()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(os.environ[ConfigurationConstants.CHORD_CONFIGURATION_FILE_ENV_VARIABLE])

    def test_successor_pointer(self):
        print("Testing successor pointers without leaves/failures.")
        print("Checking successor of 100000. Should be 300000.")
        c = None
        c = generate_xmlrpc_client(TestSuccessorsAutomated.id_ip_map[100000])
        succ = c.get_successor()
        self.assertEqual(300000, succ[0])
        print("Checking successor of 900000. Should be 100000.")
        c = generate_xmlrpc_client(TestSuccessorsAutomated.id_ip_map[900000])
        succ = c.get_successor()
        self.assertEqual(100000, succ[0])

    def test_successor_pointer_after_leave(self):
        print("Testing successor pointer updates after graceful leaves.")
        print("Stopping node 5 [id 900000].")
        TestSuccessorsAutomated._dummy_manager.stop_specific_node(4)
        print("Checking successor of node 4 [id 700000]. Should be 100000.")
        c = None
        c = generate_xmlrpc_client(TestSuccessorsAutomated.id_ip_map[700000])
        succ = c.get_successor()
        self.assertEqual(100000, succ[0])
        print("Starting back node 5 [id 900000].")
        TestSuccessorsAutomated._dummy_manager.start_specific_node(4)

    def test_successor_pointer_after_crash(self):
        print("Testing successor pointer updates/stabilization after node crash.")
        print("Crashing node 5 [id 900000].")
        TestSuccessorsAutomated._dummy_manager.stop_specific_node_without_leave(4)
        time.sleep(5)
        print("Checking successor of node 4 [id 700000]. Should be 100000.")
        c = None
        c = generate_xmlrpc_client(TestSuccessorsAutomated.id_ip_map[700000])
        succ = c.get_successor()
        self.assertEqual(100000, succ[0])
        print("Starting back node 5 [id 900000].")
        TestSuccessorsAutomated._dummy_manager.start_specific_node(4)
