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
    Represent every entry in the finger table of the node.
    Contains basic attributes like ip, key(identifier) and port.
    """

    def __init__(self, ip, identifier, port, finger_number, my_chord_server_node_id):
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
        return "| {} | {}   | {} | {}     | {}     | {}      |\n".format(self._ip, self._identifier, self._port, self.start, self.node,
                                                          self._finger_number)

    def get_ip(self):
        return self._ip

    def get_identifier(self):
        return self._identifier

    def get_port(self):
        return self._port

    def get_finger_number(self):
        return self._finger_number

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

    def get_connection_string(self):
        return self._connection_string

    def set_connection_string(self, connection_string):
        self._connection_string = connection_string

    def get_xml_client(self):
        return self.xml_client

    def set_finger_number(self, finger_number):
        self._finger_number = finger_number
        self.start = (self._my_chord_server_node_id + (2 ** (self._finger_number - 1))) % (2 ** self._config.get_m_bits())

    def create_copy(self, my_chord_server_id=None):
        if my_chord_server_id:
            return Finger(self.get_ip(), self.get_identifier(), self.get_port(), self.get_finger_number(),
                          my_chord_server_id)

        else:
            return Finger(self.get_ip(), self.get_identifier(), self.get_port(), self.get_finger_number(),
                          self._my_chord_server_node_id)

    @staticmethod
    def go_back_n_test(node_id, i, m):

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
        self._table_size = size
        self._table = [None]*self._table_size

    def get_max_table_size(self) -> int:
        """
        Returns the size of the finger table, basically m bits.
        :return: size of the finger table (int)
        """
        return self._table_size

    def get_table_size(self) -> int:
        """
        Get the current table size. ie No. of fingers present in the table.
        :return: table size at present, (int)
        """
        return len(self._table)

    def append_new_finger(self, finger: Finger) -> None:
        """
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
        Updates the finger at position i of the finger table with a new object of Finger class.
        :param i: ith location
        :param finger: Finger class object representing finger
        :return: None
        """
        self._table[i] = finger

    def get_finger_ith(self, i):
        """
        Returns the ith finger of the finger table.
        :param i: ith index
        :return: ith Finger of the finger table.
        """
        return self._table[i]

    def ith_finger_exist(self, i):
        return self._table[i]

    def __str__(self):

        s = "Finger Table\n"
        s += "| IP | Identifier | Port | Start | Node | Finger Number |\n"
        for finger in self._table:
            s += str(finger)
        return s


class Node(object):

    def __init__(self, node_id, node_ip, bootstrap_node=None):

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

        self._set_default_node_parameters()

        self._store = {}

    def i_start(self, node_id, i):
        start = (node_id + (2 ** (i - 1))) % (2 ** self._config.get_m_bits())
        return start

    def go_back_n(self, node_id, i):

        diff = node_id - i

        if diff >= 0:
            return diff
        else:
            return node_id + (2 ** self._config.get_m_bits() - i)

    def _set_default_node_parameters(self) -> None:

        self.predecessor = None
        self.successor = None

    def set_predecessor(self, predecessor) -> None:
        self.predecessor = predecessor

    def set_successor(self, successor, stabilization=False) -> None:
        logger.info("Setting successor for this node to {}.".format(successor))

        if not stabilization:
            self.successor = successor

        # if set_pred:
        #     self.set_predecessor(self.find_predecessor(self.get_node_id()))

        self.successor_list[0] = self.successor

        i = 1
        while i < 3:
            intermediate_client = self.get_xml_client(self.successor_list[i-1])
            try:
                intermediate_client.get_node_id()
                self.successor_list[i] = intermediate_client.get_successor()
            except:
                self.successor_list[i-1] = self.successor_list[i]
                if i == 1:
                    self.successor = self.successor_list[i]
                    self.update_finger_table(self.get_successor(), 0, True)

                    try:
                        intermediate_client_for_predecessor = self.get_xml_client(self.get_successor())
                        intermediate_client_for_predecessor.get_node_id()
                        intermediate_client_for_predecessor.set_predecessor((self.get_node_id(), self.get_connection_string()))
                    except:
                        logger.exception("Will try again updating the predecessor.")
                    self.replicate_keys_to_successors()

            i += 1

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
        Performs the three steps at the join of the node.
        1. Init the finger table.
        2. Update other nodes of the join.
        3. Notify higher layer software.
        (Step 3 not implemented in the initial version.)
        :return: None
        """

        logger.info("My id {}".format(self.get_node_id()))
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
            self.set_predecessor(predecessor=(self.get_node_id(),
                                              self.get_node_ip() + ":" + str(self.get_port())))
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

                #self.set_predecessor(nprime.find_predecessor(self.get_node_id()))
                self.set_successor(self.get_xml_client(self.get_predecessor()).get_successor())
                logger.info("Found successor: " + str(self.get_successor()))
                #self.set_successor(self.get_xml_client(self.get_predecessor()).get_successor())
                    #set_successor((self.get_node_id(), self.get_connection_string()), True)

                logger.info("Initializing the finger table.")
                self._init_finger_table(nprime)
                logger.info("Finger table initialized successfully.")
                logger.info("Starting to update others.")
                self._update_others()
                logger.info("Successfully updated others about this join.")

                #(self.get_xml_client(self.get_predecessor())).set_successor(
                 #   (self.get_node_id(), self.get_connection_string()))

                logger.info("Updating this node's successor's predecessor pointer to this node.")
                (self.get_xml_client(self.get_successor())).set_predecessor(
                    (self.get_node_id(), self.get_connection_string()))
                logger.info("Update successful.")
                logger.info("Updating this node's predecessor's successor pointer to this node.")
                (self.get_xml_client(self.get_predecessor())).set_successor(
                    (self.get_node_id(), self.get_connection_string()))
                logger.info("Update successful.")

                self.initialize_store()
                self.replicate_keys_to_successors()

                # move keys in (predecessor, n] from successor
            except Exception as e:
                traceback.print_exc()
                print("Invalid bootstrap server provided or failed to join the p2p system.")
                exit(1)

        logger.info(str(self._finger_table))
        logger.info("Join successful.")

    @staticmethod
    def get_xml_client(node):
        return xmlrpc.client.ServerProxy("http://" + node[1] + "/RPC2")

    def _init_finger_table(self, bootstrap_server):

        successor = self.get_successor()

        # new
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

            logger.info("Setting finger {}.".format(i+2))

            if self.in_bracket(self.i_start(self.get_node_id(), i+2),
                               [self.get_node_id(), self._finger_table.get_finger_ith(i).node],
                               type='l'):

                logger.info("{} belongs [{},{}).".format(
                    self.i_start(self.get_node_id(), i + 2),
                    self.get_node_id(),
                    self._finger_table.get_finger_ith(i).node
                ))

                logger.info("Setting finger {} from finger {}.".format(i+2, i+1))

                finger = self._finger_table.get_finger_ith(i)
                new_finger = finger.create_copy(my_chord_server_id=self.get_node_id())
                new_finger.set_finger_number(i+2)
                new_finger.set_node(finger.node)

                self._finger_table.update_finger_at_ith_position(i+1, new_finger)
            else:
                entry = bootstrap_server.find_successor(self.i_start(self.get_node_id(), i+2))
                logger.info("Setting finger {} with start {} to {}.".format(i+2, self.i_start(self.get_node_id(), i+2), str(entry)))
                finger = Finger(ip=entry[1].split(":")[0], identifier=entry[0],
                                finger_number=i+2, port=entry[1].split(":")[1],
                                my_chord_server_node_id=self.get_node_id())
                finger.set_node(entry[0])
                self._finger_table.update_finger_at_ith_position(i+1, finger)

    def _update_others(self):

        logger.info("Starting to update others.")

        for i in range(self._config.get_m_bits()):

            p = self.find_predecessor(self.go_back_n(self.get_node_id(), 2**(i)))

            logger.info("Predecessor of " + str(self.go_back_n(self.get_node_id(), 2**(i))) + " is : " + str(p) + ": " + str(i))
            client = xmlrpc.client.ServerProxy('http://' + p[1] + '/RPC2')

            client.update_finger_table((self.get_node_id(), self.get_connection_string()), i)

        logger.info("Finished updating others.")

    def update_finger_table(self, s, i, for_leave=False):

        if for_leave:
            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i + 1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            return

        if s[0] != self.get_node_id() and self.in_bracket(s[0], [self.get_node_id(), self._finger_table.get_finger_ith(i).node], type='l'):

            logger.info("Updating finger table of node {} and finger number {}.".format(self.get_node_id(),i))

            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i+1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            p = self.get_predecessor()

            while True:
                try:
                    if (not p) or p[1] == self.get_connection_string():
                        logger.info("{} : Predecessor same as node.".format(self.get_node_id()))

                        p_client = self
                    else:
                        logger.info("Update finger table for node id {} and finger number {}.".format(p[0], i))
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
        logger.info("Finding successor for {}.".format(identifier))
        predecessor = self.find_predecessor(identifier)
        predecessor_client = xmlrpc.client.ServerProxy('http://' + predecessor[1] + '/RPC2')
        logger.info("Found successor of {} : {}.".format(identifier, str(predecessor_client.get_successor())))
        return predecessor_client.get_successor()

    def find_predecessor(self, identifier):

        logger.info("Finding predecessor of {}.".format(identifier))
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
        logger.info("Found predecessor of {} : {}.".format(identifier, node.get_node_id()))
        return node.get_node_id(), node.get_connection_string()

    def closest_preceding_finger(self, identifier):
        logger.info("Finding closest preceding finger of {}.".format(identifier))
        m = self._config.get_m_bits()
        for i in range(m-1, -1, -1):
            if self.in_bracket(self._finger_table.get_finger_ith(i).node, [self.get_node_id(), identifier],
                               "o"):
                logger.info("Closest preceding finger of {} : {}.".format(identifier, self._finger_table.get_finger_ith(i).node))
                return self._finger_table.get_finger_ith(i).node, \
                       self._finger_table.get_finger_ith(i).get_connection_string()
        logger.info("Closest preceding finger of {} : {}.".format(identifier, self.get_node_id()))
        return self.get_node_id(), self.get_connection_string()

    def leave(self):

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

        logger.info("{}, {}, {}".format(num, limits[0], limits[1], type))

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
        if (lower == higher):
            in_between_flag = True
        else:
            if (lower < higher):
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
        returned = object.__getattribute__(self, name)
        if inspect.isfunction(returned) or inspect.ismethod(returned):
            if function_debug:
                print('called ', returned.__name__)
        return returned

    def set(self, key, hash_it=True):
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        return (self.get_xml_client(self.find_successor(key))).set_key(key)

    def get(self, key, hash_it=True):
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        return (self.get_xml_client(self.find_successor(key))).get_key(key)

    def delete(self, key, hash_it=True):
        if hash_it:
            key = consistent_hashing.Consistent_Hashing.get_modulo_hash(key, self._config.get_m_bits())
        return (self.get_xml_client(self.find_successor(key))).delete_key(key)

    def set_key(self, key):
        self._store[key] = True
        if self.get_node_id() != self.get_successor()[0]:
            self.replicate_single_key_to_successor(key)
        return self.get_node_id(), self.get_connection_string()

    def get_key(self, key):
        if key in self._store:
            return self.get_node_id(), self.get_connection_string()
        return None

    def delete_key(self, key):

        if key in self._store:
            del self._store[key]
            if self.get_node_id() != self.get_successor()[0]:
                self.del_key_from_successor(key)
            return self.get_node_id(), self.get_connection_string()
        return None

    def get_store(self):
        return self._store

    def initialize_store(self):
        self._store = ast.literal_eval(self.get_xml_client(self.get_successor()).get_transfer_data(self.get_node_id()))

    def get_transfer_data(self, node_id):

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
        self.get_xml_client(self.get_successor()).receive_keys_before_leave(str(self._store))

    def receive_keys_before_leave(self, store):

        store = ast.literal_eval(store)

        for key in store:
            self._store[key] = store[key]

    def stabilize_paper(self):
        logger.info("Starting stabilization.")
        successor_client = self.get_xml_client(self.get_successor())
        x = successor_client.get_predecessor()
        if self.in_bracket(x[0], [self.get_node_id(), self.get_successor()[0]], 'o'):
            self.set_successor(x)
        successor_client.notify((self.get_node_id(), self.get_connection_string()))
        logger.info("Finished stabilization.")

    def notify(self, nprime):
        if (not self.get_predecessor()) or \
                self.in_bracket(nprime[0], [self.get_predecessor()[0], self.get_node_id()], 'o'):
            self.set_predecessor(nprime)

    def fix_fingers(self):
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
        self.set_successor(self.successor, True)

    def replicate_keys_to_successors(self, store=None):
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
        store = {key: False}
        self.replicate_keys_to_successors(store)

    def del_key_from_successor(self, key):
        if key in self._store:
            del self._store[key]

    def replication_stabilization(self):

        """
        For all the keys which are false in this node, if they are false in my predecessor as well,
        then my predecessor is no more the original owner of this key, hence this node is not
        the correct replica for this key.
        :return: None
        """

        false_store = {}
        for key in self._store:
            if not self._store[key]:
                false_store[key] = True

        keys_to_be_removed = self.get_xml_client(self.get_predecessor()).get_non_owned_keys(str(false_store))

        for key in keys_to_be_removed:
            del self._store[key]

    def get_non_owned_keys(self, false_store):
        false_store = ast.literal_eval(false_store)
        non_owned_keys = []
        for key in false_store:
            if key not in self._store:
                pass
            elif not self._store[key]:
                non_owned_keys.append(key)

        return non_owned_keys
