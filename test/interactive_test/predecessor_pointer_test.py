"""
Author: Adarsh Trivedi
This module tests for correctness of predecessor pointers of nodes by first performing joins on 5 nodes,
then doing graceful leaves and crashes of nodes and checking for correctness of the predecessor
pointers. The tests are interactive and are designed so that humans can test the code by generating
scenarios and inputting correct expected values. Test names are intuitive.
The tests require some chord nodes to be active. For this use test.start_dummy_nodes module to
spawn 5 nodes on the system for testing. The nodes will be started on port 5001-5005. The start_dummy_nodes
module provides functionality to start, crash, leave particular nodes to run tests successfully.

Along with predecessor pointer correctness this module also verifies stabilization protocol,
since pointer correctness after crashes are the responsibility stabilization protocol.
"""


import unittest
import xmlrpc.client


def generate_xmlrpc_client(connection_string):
    return xmlrpc.client.ServerProxy("http://" + connection_string + "/RPC2")


class TestPredecessor(unittest.TestCase):

    def test_predecessor_pointer(self):

        run = True

        while run:
            print("Testing predecessor pointers in normal scenario.")
            node_id = input("Predecessor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                pred = c.get_predecessor()
                try:
                    expected = int(input("Enter expected value:"))
                except:
                    print("Make sure it's integer.")
                    continue
            except:
                if node_id.strip() == "stop":
                    run = False
                else:
                    print("Invalid input")
                    continue
            if run:
                self.assertEqual(expected, pred[0])

    def test_predecessor_pointer_after_leave(self):

        run = True

        while run:
            print("Testing predecessor pointers after leave scenario.")
            node_id = input("predecessor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                pred = c.get_predecessor()
                try:
                    expected = int(input("Enter expected value:"))
                except:
                    print("Make sure it's integer.")
                    continue
            except:
                if node_id.strip() == "stop":
                    run = False
                else:
                    print("Invalid input")
                    continue
            if run:
                self.assertEqual(expected, pred[0])

    def test_predecessor_pointer_after_crash(self):

        run = True

        while run:
            print("Testing predecessor pointers after crash.")
            node_id = input("predecessor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                pred = c.get_predecessor()
                try:
                    expected = int(input("Enter expected value:"))
                except:
                    print("Make sure it's integer.")
                    continue
            except:
                if node_id.strip() == "stop":
                    run = False
                else:
                    print("Invalid input")
                    continue
            if run:
                print(expected,pred)
                self.assertEqual(expected, pred[0])


if __name__ == "__main__":
    unittest.main()
