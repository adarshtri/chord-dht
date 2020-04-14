import unittest
import xmlrpc.client


def generate_xmlrpc_client(connection_string):
    return xmlrpc.client.ServerProxy("http://" + connection_string + "/RPC2")


class TestSuccessors(unittest.TestCase):

    def test_successor_pointer(self):

        run = True

        while run:
            print("Testing successor pointers in normal scenario.")
            node_id = input("Successor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                succ = c.get_successor()
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
                self.assertEqual(expected, succ[0])

    def test_successor_pointer_after_leave(self):

        run = True

        while run:
            print("Testing successor pointers after leave scenario.")
            node_id = input("Successor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                succ = c.get_successor()
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
                self.assertEqual(expected, succ[0])

    def test_successor_pointer_after_crash(self):

        run = True

        while run:
            print("Testing successor pointers after crash.")
            node_id = input("Successor of [provide something like localhost:5001] or stop:")

            try:
                c = generate_xmlrpc_client(node_id)
                c.get_node_id()
                succ = c.get_successor()
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
                self.assertEqual(expected, succ[0])


if __name__ == "__main__":
    unittest.main()
