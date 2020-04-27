""" CHORD NODE Implementation

The module encapsulates 3 classes namely Finger, FingerTable and Node.
The classes represents as their name suggests.

Authors: Adarsh Trivedi, Ishan Goel
"""
from utilities.configuration import ConfigurationManager
import xmlrpc.client
import traceback
import inspect
from utilities import consistent_hashing
import ast
import random
from utilities.app_logging import Logging

logger = Logging.get_logger(__name__)
debug = False
function_debug = False


class Finger(object):

    """
    Author: Adarsh Trivedi
    Represent every entry in the finger table of the node.
    Contains basic attributes like ip, key(identifier) and port.
    """

    def __init__(self, ip, identifier, port, finger_number, my_chord_server_node_id):
        """
        Author: Adarsh Trivedi
        :param ip: Ip of the finger pointing to node.
        :param identifier: Hash ID of the finger pointing to node.
        :param port: Port of the finger pointing to node.
        :param finger_number: Finger number in the finger table.
        :param my_chord_server_node_id: Node id of the chord node of which this finger is in.
        """
        self._my_chord_server_node_id = my_chord_server_node_id
        self._config = ConfigurationManager.get_configuration()
        self._ip = ip
        self._identifier = identifier
        self._port = port
        self._finger_number = finger_number
        self.start = (self._my_chord_server_node_id + (2**(self._finger_number-1))) % (2**self._config.get_m_bits())

        # should be successor of _start
        self.node = None
        self.xml_client = None
        self._connection_string = ip + ":" + str(port)

    def __str__(self):
        """
        Author: Adarsh Trivedi
        Gives string representation of the finger. Useful in logging and debugging.
        :return: str
        """
        return "| {} | {}   | {} | {}     | {}     | {}      |\n".format(self._ip, self._identifier, self._port, self.start, self.node,
                                                          self._finger_number)
    """
    Author: Adarsh Trivedi
    Getter functions of the class properties.
    """
    def get_ip(self):
        return self._ip

    def get_identifier(self):
        return self._identifier

    def get_port(self):
        return self._port

    def get_finger_number(self):
        return self._finger_number

    def get_connection_string(self):
        return self._connection_string

    def get_xml_client(self):
        return self.xml_client

    """
    Author: Adarsh Trivedi
    Setter functions of class properties.
    """
    def set_id(self, id):
        self._identifier = id

    def set_port(self, port):
        self._port = port

    def set_ip(self, ip):
        self._ip = ip

    def set_node(self, node):
        self.node = node

    def set_xml_client(self, client):
        self.xml_client = client

    def set_connection_string(self, connection_string):
        self._connection_string = connection_string

    def set_finger_number(self, finger_number):
        self._finger_number = finger_number
        self.start = (self._my_chord_server_node_id + (2 ** (self._finger_number - 1))) % (2 ** self._config.get_m_bits())

    def create_copy(self, my_chord_server_id=None):
        """
        Author: Adarsh Trivedi
        Creates a copy of this self Finger instance.
        :param my_chord_server_id: Only expects which chord node finger belongs to.
        :return: Finger
        """
        if my_chord_server_id:
            return Finger(self.get_ip(), self.get_identifier(), self.get_port(), self.get_finger_number(),
                          my_chord_server_id)

        else:
            return Finger(self.get_ip(), self.get_identifier(), self.get_port(), self.get_finger_number(),
                          self._my_chord_server_node_id)

    @staticmethod
    def go_back_n_test(node_id, i, m):

        """
        Helper functions to move backwards in the chord circle.
        Author: Adarsh Trivedi
        :param node_id: Start id
        :param i: Used in formula to move back.
        :param m: Used in formula to move back.
        :return: int
        """

        diff = node_id - i

        if diff >= 0:
            return diff
        else:
            return node_id + (2 ** m - i)


class FingerTable(object):

    """
    Represents the finger table for each node. Encapsulates some helper functions
    for the finger table.
    """

    def __init__(self, size):
        """
        Author: Adarsh Trivedi
        :param size: Size of the table. This is pre-decided based on m-bits.
        """
        self._table_size = size
        self._table = [None]*self._table_size

    def get_max_table_size(self) -> int:
        """
        Author: Adarsh Trivedi
        Returns the size of the finger table, basically m bits.
        :return: size of the finger table (int)
        """
        return self._table_size

    def get_table_size(self) -> int:
        """
        Author: Adarsh Trivedi
        Get the current table size. ie No. of fingers present in the table.
        :return: table size at present, (int)
        """
        return len(self._table)

    def append_new_finger(self, finger: Finger) -> None:
        """
        Author: Adarsh Trivedi
        Adds a new finger to the finger table. Simply appends the new finger
        to the table.
        :param finger:
        :return:
        """
        if self.get_table_size() >= self.get_max_table_size():
            pass
        else:
            self._table.append(finger)

    def update_finger_at_ith_position(self, i: int, finger: Finger) -> None:
        """
        Author: Adarsh Trivedi
        Updates the finger at position i of the finger table with a new object of Finger class.
        :param i: ith location
        :param finger: Finger class object representing finger
        :return: None
        """
        self._table[i] = finger

    def get_finger_ith(self, i):
        """
        Author: Adarsh Trivedi
        Returns the ith finger of the finger table.
        :param i: ith index
        :return: ith Finger of the finger table.
        """
        return self._table[i]

    def ith_finger_exist(self, i):
        """
        Author: Adarsh Trivedi
        :param i: ith Finger
        :return: boolean
        """
        return self._table[i]

    def __str__(self):

        """
        Author: Adarsh Trivedi
        :returns: String representation of the finger table. Useful in logging/debugging.
        :return: str
        """

        s = "Finger Table\n"
        s += "| IP | Identifier | Port | Start | Node | Finger Number |\n"
        for finger in self._table:
            s += str(finger)
        return s


class Node(object):

    """
    This is the class which implements all the methods described in the paper for every chord node.

    Important methods:

    1. Join
    2. Find Successor
    3. Find Predecessor
    4. Update Others
    5. Initialize Finger Table
    6. Stabilization
    7. Fix Finger Table
    8. Get
    9. Set
    10. Delete
    """

    def __init__(self, node_id, node_ip, bootstrap_node=None):

        """
        Author: Adarsh Trivedi
        :param node_id: Hash node id, represents id on the chord ring.
        :param node_ip: IP of the node.
        :param bootstrap_node: Bootstrap server to start with. Can be None for new chord ring formation.
        """

        self._node_id = node_id
        self._node_ip = node_ip
        self._config = ConfigurationManager.get_configuration()
        self._port = self._config.get_socket_port()
        self._bootstrap_server = bootstrap_node
        self._finger_table = FingerTable(size=self._config.get_m_bits())
        self.predecessor = None
        self.successor = None
        self.successor_list = [(self.get_node_id(), self.get_connection_string())]*3

        if not bootstrap_node:
            logger.info("Creating new node, with no bootstrap server.")
            logger.info("Node ip: {}".format(node_ip))
            logger.info("Node id: {}".format(str(node_id)))
        else:
            logger.info("Creating new node. Node ip {}. Node id {}.".format(node_ip, node_id))

        self._set_default_node_parameters()

        self._store = {}

    def i_start(self, node_id, i) -> int:
        """
        Author: Adarsh Trivedi
        Helper function.
        :param node_id: Current node id.
        :param i: node_id + 2^i
        :return: node_id + 2^i
        """
        start = (node_id + (2 ** (i - 1))) % (2 ** self._config.get_m_bits())
        return start

    def go_back_n(self, node_id, i) -> int:
        """
        Author: Adarsh Trivedi
        Helper functions.
        :param node_id: Current node_id
        :param i: How many steps to move back.
        :return: id after moving specified steps back.
        """
        diff = node_id - i

        if diff >= 0:
            return diff
        else:
            return node_id + (2 ** self._config.get_m_bits() - i)

    """
    Author: Adarsh Trivedi
    Default setter functions.
    """
    def _set_default_node_parameters(self) -> None:

        self.predecessor = None
        self.successor = None

    def set_predecessor(self, predecessor) -> None:
        self.predecessor = predecessor

    def set_successor(self, successor, stabilization=False) -> None:

        """
        Author: Adarsh Trivedi
        This function is used for both successor setting and stabilization protocol.
        Second parameter of the function controls which functionality to execute.
        :param successor: Successor to be set for this instance.
        :param stabilization: bool
        :return: None
        """

        logger.info("Setting successor for this node to {}.".format(successor))

        # if normal set call, set the successor to specified value.
        # stabilization call passes "successor" as what node already has and makes no sense to set again.
        if not stabilization:
            self.successor = successor

        # update the successor list's first value to the successor
        self.successor_list[0] = self.successor

        # the implementation maintains 3 successors in the successor list. As a part of stabilization
        # we try to make sure these pointers are correct.
        i = 1
        while i < 3:
            # get the client for the previous element in the successor list
            intermediate_client = self.get_xml_client(self.successor_list[i-1])
            try:
                # if client obtained successfully then set current value of successor list
                # to the successor of the previous element in successor list
                intermediate_client.get_node_id()
                self.successor_list[i] = intermediate_client.get_successor()
            except:
                # if client couldn't be obtained then this successor element should be the previous
                # successor element since previous successor element is not valid
                self.successor_list[i-1] = self.successor_list[i]
                if i == 1:
                    # if i is 1 and client for 0 was not obtained successfully that means
                    # we have to change the successor also of this node
                    # since successor_list[0] is the successor
                    logger.info("Suspect a crash for node [{}].".format(self.get_successor()))
                    self.successor = self.successor_list[i]
                    self.update_finger_table(self.get_successor(), 0, True)

                    # update the predecessor as well
                    try:
                        intermediate_client_for_predecessor = self.get_xml_client(self.get_successor())
                        intermediate_client_for_predecessor.get_node_id()
                        intermediate_client_for_predecessor.set_predecessor((self.get_node_id(), self.get_connection_string()))
                    except:
                        logger.exception("Will try again updating the predecessor.")
                    # as successor was changed replicate the keys to new successors in the successor_list
                    self.replicate_keys_to_successors()
            i += 1

    """
    Author: Adarsh Trivedi
    Getter functions of the class attributes.
    """
    def get_successor(self):
        return self.successor

    def get_predecessor(self):
        return self.predecessor

    def get_node_id(self):
        return self._node_id

    def get_connection_string(self):
        return self._node_ip + ":" + str(self._port)

    def get_port(self):
        return self._port

    def get_node_ip(self):
        return self._node_ip

    def get_successor_list(self):
        return self.successor_list

    def join(self) -> None:

        """
        Author: Ishan Goel(chord implementation) / Adarsh Trivedi (node communication with XML RPC)
        Performs the three steps at the join of the node.
        1. Init the finger table.
        2. Update other nodes of the join.
        3. Notify higher layer software.
        (Step 3 not implemented in the initial version.)
        :return: None
        """

        logger.info("Starting join ....")

        if not self._bootstrap_server:
            logger.warning("No bootstrap server provided. Starting a new chord ring.")
            logger.info("Initializing the finger table.")
            for i in range(1, self._config.get_m_bits()+1):
                finger = Finger(ip=self._config.get_chord_server_ip(),
                                identifier=self._node_id,
                                port=self._config.get_socket_port(),
                                finger_number=i,
                                my_chord_server_node_id=self.get_node_id())

                finger.set_node(self.get_node_id())
                finger.set_xml_client(xmlrpc.client.ServerProxy(
                    'http://' + self.get_node_ip() + ":" + str(self.get_port()) + '/RPC2'))

                self._finger_table.update_finger_at_ith_position(i-1, finger)
            logger.info("Predecessor {}.".format(self.get_node_id()))
            self.set_predecessor(predecessor=(self.get_node_id(),
                                              self.get_node_ip() + ":" + str(self.get_port())))
            logger.info("Successor {}.".format(self.get_node_id()))
            self.set_successor(successor=(self.get_node_id(),
                                          self.get_node_ip() + ":" + str(self.get_port())))
            logger.info("No need to update others. This is the only node is p2p system.")
        else:
            logger.info("Joining an existing chord ring with bootstrap server {}.".format(self._bootstrap_server))
            try:

                nprime = xmlrpc.client.ServerProxy('http://' + self._bootstrap_server + '/RPC2')
                nprime.get_finger_table()
                self.set_predecessor(nprime.find_predecessor(self.get_node_id()))

                logger.info("Found predecessor: " + str(self.get_predecessor()))

                self.set_successor(self.get_xml_client(self.get_predecessor()).get_successor())
                logger.info("Found successor: " + str(self.get_successor()))

                logger.info("Initializing the finger table.")
                self._init_finger_table(nprime)
                logger.info("Finger table initialized successfully.")
                logger.info("Starting to update others.")
                self._update_others()
                logger.info("Successfully updated others about this join.")

                logger.info("Updating this node's successor's predecessor pointer to this node.")
                (self.get_xml_client(self.get_successor())).set_predecessor(
                    (self.get_node_id(), self.get_connection_string()))
                logger.info("Update successful.")
                logger.info("Updating this node's predecessor's successor pointer to this node.")
                (self.get_xml_client(self.get_predecessor())).set_successor(
                    (self.get_node_id(), self.get_connection_string()))
                logger.info("Update successful.")

                logger.info("Initializing hash table to get this node's keys.")
                self.initialize_store()
                logger.info("Hash table initialized.")
                logger.info("Starting replication to successors.")
                self.replicate_keys_to_successors()
                logger.info("Replication successful.")

                # move keys in (predecessor, n] from successor
            except Exception as e:
                traceback.print_exc()
                print("Invalid bootstrap server provided or failed to join the p2p system.")
                exit(1)

        logger.info(str(self._finger_table))
        logger.info("Join successful.")

    @staticmethod
    def get_xml_client(node) -> xmlrpc.client.ServerProxy:
        """
        Author: Adarsh Trivedi
        Helper function. Creates an XML RPC client for the passed node.
        :param node: Node to create client for.
        :return: XML RPC Client
        """
        return xmlrpc.client.ServerProxy("http://" + node[1] + "/RPC2")

    def _init_finger_table(self, bootstrap_server):

        """
        Author: Ishan Goel (chord implementation) / Adarsh Trivedi (Node Communication code)
        :param bootstrap_server: Bootstrap server
        :return: None
        """

        successor = self.get_successor()

        self.set_predecessor(self.get_xml_client(successor).get_predecessor())

        logger.info("Initializing the first finger to successor node {}.".format(str(self.get_successor())))
        finger = Finger(ip=successor[1].split(":")[0], identifier=successor[0],
                        port=successor[1].split(":")[1], finger_number=1, my_chord_server_node_id=self.get_node_id())
        finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + successor[1] + '/RPC2'))
        finger.set_node(successor[0])
        self._finger_table.update_finger_at_ith_position(i=0, finger=finger)
        self._finger_table.get_finger_ith(0)._node = successor[0]

        self.set_successor(successor)

        for i in range(self._config.get_m_bits()-1):

            if self.in_bracket(self.i_start(self.get_node_id(), i+2),
                               [self.get_node_id(), self._finger_table.get_finger_ith(i).node],
                               type='l'):

                finger = self._finger_table.get_finger_ith(i)
                new_finger = finger.create_copy(my_chord_server_id=self.get_node_id())
                new_finger.set_finger_number(i+2)
                new_finger.set_node(finger.node)

                self._finger_table.update_finger_at_ith_position(i+1, new_finger)
            else:
                entry = bootstrap_server.find_successor(self.i_start(self.get_node_id(), i+2))
                finger = Finger(ip=entry[1].split(":")[0], identifier=entry[0],
                                finger_number=i+2, port=entry[1].split(":")[1],
                                my_chord_server_node_id=self.get_node_id())
                finger.set_node(entry[0])
                self._finger_table.update_finger_at_ith_position(i+1, finger)

    def _update_others(self):

        """
        Author: Ishan Goel (chord implementation) / Adarsh Trivedi (Node communication)
        :return: None
        """

        logger.info("Starting to update others.")

        for i in range(self._config.get_m_bits()):

            p = self.find_predecessor(self.go_back_n(self.get_node_id(), 2**(i)))
            client = xmlrpc.client.ServerProxy('http://' + p[1] + '/RPC2')
            client.update_finger_table((self.get_node_id(), self.get_connection_string()), i)

        logger.info("Finished updating others.")

    def update_finger_table(self, s, i, for_leave=False):

        """
        Author: Ishan Goel (chord implementation) / Adarsh Trivedi (chord implementation and Node Communication)
        :param s: Source node.
        :param i: Which finger to update.
        :param for_leave: This parameter is used to control whether this function was called during join (leave=False)
                          or during graceful leave. For graceful leave we have to update the first finger (which points
                          to successor to appropriate node. Rest is handled by stabilization protocol).
        :return: None
        """

        if for_leave:
            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i + 1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            return

        if s[0] != self.get_node_id() and self.in_bracket(s[0], [self.get_node_id(), self._finger_table.get_finger_ith(i).node], type='l'):

            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i+1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            p = self.get_predecessor()

            while True:
                try:
                    if (not p) or p[1] == self.get_connection_string():
                        p_client = self
                        # here don't call update_finger_table as it will go to infinite recursion.
                    else:
                        p_client = xmlrpc.client.ServerProxy('http://' + p[1] + '/RPC2')
                        p_client.update_finger_table(s, i)
                    break
                except Exception as e:
                    print(e)
                    continue

            return None

    def get_finger_table(self):
        return str(self._finger_table)

    def find_successor(self, identifier):
        """
        Author: Ishan Goel
        :param identifier: id whose successor to be found.
        :return: Successor
        """
        predecessor = self.find_predecessor(identifier)
        predecessor_client = xmlrpc.client.ServerProxy('http://' + predecessor[1] + '/RPC2')
        return predecessor_client.get_successor()

    def find_predecessor(self, identifier):

        """
        Author: Ishan Goel
        :param identifier: Id whose predecessor to be found.
        :return: Predecessor
        """

        node = xmlrpc.client.ServerProxy('http://' + self.get_connection_string() + '/RPC2')

        if node.get_node_id() == node.get_successor()[0]:
            return node.get_node_id(), node.get_connection_string()

        while not self.in_bracket(identifier, [node.get_node_id(), node.get_successor()[0]], type='r'):

            node = node.closest_preceding_finger(identifier)
            connection_string = node[1]

            while True:
                try:
                    node = xmlrpc.client.ServerProxy('http://' + connection_string + '/RPC2')
                    connection_string = node.get_connection_string()
                    break
                except Exception as e:
                    continue
        return node.get_node_id(), node.get_connection_string()

    def closest_preceding_finger(self, identifier):

        """
        Author: Ishan Goel / Adarsh Trivedi
        Returns the closest finger in the finger table preceding the id.
        :param identifier: ID
        :return: Closest finger.
        """

        m = self._config.get_m_bits()
        for i in range(m-1, -1, -1):
            if self.in_bracket(self._finger_table.get_finger_ith(i).node, [self.get_node_id(), identifier],
                               "o"):
                return self._finger_table.get_finger_ith(i).node, \
                       self._finger_table.get_finger_ith(i).get_connection_string()
        return self.get_node_id(), self.get_connection_string()

    def leave(self):

        """
        Author: Adarsh Trivedi
        Performs a graceful leave of the node. Updates this node's successor and predecessor's respective
        predecessor and successor pointers. This node is in between it's successor and predecessor. They
        shouldn't point to this node.
        This function also transfers its keys to responsible node.
        :return: None
        """

        logger.info("Starting to leave the system.")
        logger.info("Setting predecessor's [{}] successor to this node's successor [{}].".
                    format(self.get_predecessor(), self.get_successor()))
        self.get_xml_client(self.get_predecessor()).set_successor(self.get_successor())
        logger.info("Setting successor's [{}] predecessor to this node's predecessor [{}].".
                    format(self.get_successor(), self.get_predecessor()))
        self.get_xml_client(self.get_successor()).set_predecessor(self.get_predecessor())
        logger.info("Updating 1st finger (successor) to this node's successor.")
        self.get_xml_client(self.get_predecessor()).update_finger_table(self.get_successor(), 0, True)
        logger.info("Transferring keys to responsible node.")
        self.transfer_before_leave()
        logger.info("Node {} left the system successfully.".format(self.get_node_id()))

    def in_bracket(self, num, limits, type='c'):

        """
        Author: Ishan Goel
        Helper function. Implements belongs_to mathematical function in context of a modulus style chord ring.
        :param num: id
        :param limits: boundaries
        :param type: c: closed, r: right closed, l:left closed
        :return: bool
        """

        lower, higher = limits

        if lower == num and (type == 'l' or type == 'c'):
            if debug:
                print(True)
            return True

        if higher == num and (type == 'r' or type == 'c'):
            if debug:
                print(True)
            return True

        in_between_flag = None
        if lower == higher:
            in_between_flag = True
        else:
            if lower < higher:
                in_between_flag = (lower < num) and (num < higher)
            else:
                in_between_flag = not ((higher < num) and (num < lower))

        right_touch_flag = (num == lower) and not ((type == 'c') or (type == 'l'))
        left_touch_flag = (num == higher) and not ((type == 'c') or (type == 'r'))

        return_type = in_between_flag and not (right_touch_flag or left_touch_flag)
        if debug:
            print(return_type)
        return return_type

    def __getattribute__(self, name):
        """
        Author: Adarsh Trivedi
        Helper function to print order of function calls. Used for debugging.
        :param name: Function name.
        :return: bool
        """
        returned = object.__getattribute__(self, name)
        if inspect.isfunction(returned) or inspect.ismethod(returned):
            if function_debug:
                print('called ', returned.__name__)
        return returned

    def set(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        Store the key on responsible node. Performs routing to responsible node. Doesn't perform set on itself.
        :param key: Key to be stored.
        :param hash_it: If set false, expects key to be an integer value which is not hashed before storing.
                        Expect code blast if hash_it = False and key not int. Should be handled with assertion
                        before setting.
        :return: Node on which key is stored.
        """
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        logger.info("Set request for key {} at {}.".format(key, self.get_node_id()))
        return (self.get_xml_client(self.find_successor(key))).set_key(key)

    def get(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        Get the key from the p2p network. Performs routing to responsible node. Doesn't perform get from its own store.
        :param key: Key to be retrieved.
        :param hash_it: As in set function.
        :return: Node on which the key is retrieved from.
        """
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        logger.info("Get request for key {} at {}.".format(key, self.get_node_id()))
        return (self.get_xml_client(self.find_successor(key))).get_key(key)

    def delete(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        Delete the key from the network. Performs routing to responsible node. Doesn't perform delete itself.
        :param key: Key to be deleted.
        :param hash_it: As is set function.
        :return: Node on which key was present and deleted.
        """
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        logger.info("Delete request for key {} at {}.".format(key, self.get_node_id()))
        return (self.get_xml_client(self.find_successor(key))).delete_key(key)

    def set_key(self, key):
        """
        Author: Adarsh Trivedi
        Set the key in this instance's data store.
        :param key: Key to be set
        :return: self
        """
        logger.info("Set request for key {} redirected at {}.".format(key, self.get_node_id()))
        self._store[key] = True
        if self.get_node_id() != self.get_successor()[0]:
            self.replicate_single_key_to_successor(key)
        return self.get_node_id(), self.get_connection_string()

    def get_key(self, key):
        """
        Author: Adarsh Trivedi
        Get the key in this instance's data store.
        :param key: Key to be searched.
        :return: self
        """
        logger.info("Get request for key {} redirected at {}.".format(key, self.get_node_id()))
        if key in self._store:
            return self.get_node_id(), self.get_connection_string()
        return None

    def delete_key(self, key):
        """
        Author: Adarsh Trivedi
        Delete the key from this instance's data store.
        :param key: Key to be deleted.
        :return: self
        """
        logger.info("Delete request for key {} redirected at {}.".format(key, self.get_node_id()))
        if key in self._store:
            del self._store[key]
            if self.get_node_id() != self.get_successor()[0]:
                self.del_key_from_successor(key)
            return self.get_node_id(), self.get_connection_string()
        return None

    def get_store(self):
        """
        Author: Adarsh Trivedi
        :return: This node's data store.
        """
        return self._store

    def initialize_store(self):
        """
        Author: Adarsh Trivedi
        Initialize this node's data from successor node's data store.
        :return: None
        """
        self._store = ast.literal_eval(self.get_xml_client(self.get_successor()).get_transfer_data(self.get_node_id()))

    def get_transfer_data(self, node_id):

        """
        Author: Adarsh Trivedi
        Returns key from this node which precede node_id parameter. Used during join.
        :param node_id: New node's id.
        :return: Responsible keys as dictionary.
        """

        transfer_data = {}
        keys_to_be_deleted = []

        for key in self._store:
            if self.in_bracket(key, [self.get_node_id(), node_id], 'o'):
                transfer_data[key] = True
                keys_to_be_deleted.append(key)

        for key in keys_to_be_deleted:
            del self._store[key]

        return str(transfer_data)

    def transfer_before_leave(self):
        """
        Author: Adarsh Trivedi
        Transfer this node's key to successor before graceful leave.
        :return: None
        """
        self.get_xml_client(self.get_successor()).receive_keys_before_leave(str(self._store))

    def receive_keys_before_leave(self, store):
        """
        Author: Adarsh Trivedi
        Sets current node's data store with store values received from predecessor node before
        graceful leave.
        :param store: Received store values.
        :return: None
        """
        store = ast.literal_eval(store)

        for key in store:
            self._store[key] = store[key]

    def stabilize_paper(self):
        """
        Author: Adarsh Trivedi
        Stabilization method as described in Chord Paper. Not used. Custom method used.
        :return: None
        """
        logger.info("Starting stabilization.")
        successor_client = self.get_xml_client(self.get_successor())
        x = successor_client.get_predecessor()
        if self.in_bracket(x[0], [self.get_node_id(), self.get_successor()[0]], 'o'):
            self.set_successor(x)
        logger.info("Notifying successor my this node.")
        successor_client.notify((self.get_node_id(), self.get_connection_string()))
        logger.info("Finished stabilization.")

    def notify(self, nprime):
        """
        Author: Adarsh Trivedi
        Method as described in Chord Paper. Not used most probably.
        :param nprime: None
        :return: None
        """
        if (not self.get_predecessor()) or \
                self.in_bracket(nprime[0], [self.get_predecessor()[0], self.get_node_id()], 'o'):
            self.set_predecessor(nprime)

    def fix_fingers(self):

        """
        Author: Adarsh Trivedi
        This function is called periodically as part of stabilization protocol. It selects a random
        finger from this node's finger table and checks if it is pointing to correct node or else
        correct it.
        :return: None
        """

        logger.info("Fixing finger table.")
        i = random.randint(1, self._config.get_m_bits()-1)
        finger = self._finger_table.get_finger_ith(i)
        finger = finger.create_copy()
        finger_start_successor = self.find_successor(finger.start)
        finger.set_node(finger_start_successor[0])
        finger.set_connection_string(finger_start_successor[1])
        finger.set_id(finger_start_successor[0])
        finger.set_ip(finger_start_successor[1].split(":")[0])
        finger.set_port(finger_start_successor[1].split(":")[1])
        self._finger_table.update_finger_at_ith_position(i, finger)

    def stabilize(self):
        """
        Author: Adarsh Trivedi
        This function performs the stabilization for the node.
        The stabilization should ensure that the successor pointer of
        the node is intact. To ensure that we use set_successor method with stabilization=True parameter.
        Read documentation for set_successor function for detailed functioning of stabilization is handled.
        :return: None
        """
        logger.info("Starting stabilization.")
        self.set_successor(self.successor, True)
        logger.info("Finished stabilization.")

    def replicate_keys_to_successors(self, store=None):
        """
        Author: Adarsh Trivedi
        Replicates set of keys to successors for crash handling.
        :param store: Keys to be replicated to successors.
        :return: None
        """
        for i in range(len(self.get_successor_list())):
            if not store:
                build_store = {}
                for key in self._store:
                    if self._store[key]:
                        build_store[key] = False
                self.get_xml_client(self.get_successor_list()[i]).receive_keys_before_leave(str(build_store))
            else:
                self.get_xml_client(self.get_successor_list()[i]).receive_keys_before_leave(str(store))

    def replicate_single_key_to_successor(self, key):
        """
        Author: Adarsh Trivedi
        :param key: Key to be replicated.
        :return: None
        """
        store = {key: False}
        self.replicate_keys_to_successors(store)

    def del_key_from_successor(self, key):
        """
        Author: Adarsh Trivedi
        :param key: Removes the replicated key from successors.
        :return:
        """
        if key in self._store:
            del self._store[key]

    def replication_stabilization(self):

        """
        Author: Adarsh Trivedi
        For all the keys which are false in this node, if they are false in my predecessor as well,
        then my predecessor is no more the original owner of this key, hence this node is not
        the correct replica for this key.
        :return: None
        This method is not being used at present. Needs more deliberation and experimentation before
        it can be correctly implemented.
        """

        false_store = {}
        for key in self._store:
            if not self._store[key]:
                false_store[key] = True

        keys_to_be_removed = self.get_xml_client(self.get_predecessor()).get_non_owned_keys(str(false_store))

        for key in keys_to_be_removed:
            del self._store[key]

    def get_non_owned_keys(self, false_store):
        """
        Author: Adarsh Trivedi
        Part of replication key stabilization. Delete keys from the node which are not owned by
        this node but are replicated. Not used at present.
        :param false_store: Keys which are replicated and should be deleted.
        :return: Non owned keys.
        """
        false_store = ast.literal_eval(false_store)
        non_owned_keys = []
        for key in false_store:
            if key not in self._store:
                pass
            elif not self._store[key]:
                non_owned_keys.append(key)

        return non_owned_keys
