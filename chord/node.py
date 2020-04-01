from utilities.configuration import ConfigurationManager
import xmlrpc.client
import traceback
import inspect

debug = True
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
    def i_start(node_id, i):
        start = (node_id + (2 ** (i-1))) % (2 ** ConfigurationManager.get_configuration().get_m_bits())
        return start

    @staticmethod
    def go_back_n(node_id, i):

        diff = node_id - i

        if diff >= 0:
            return diff
        else:
            return node_id + (2**ConfigurationManager.get_configuration().get_m_bits() - i)

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
        self._port = ConfigurationManager.get_configuration().get_socket_port()
        self._bootstrap_server = bootstrap_node
        self._config = ConfigurationManager.get_configuration()
        self._finger_table = FingerTable(size=self._config.get_m_bits())

        if debug:
            if not bootstrap_node:
                print("Creating new node, with no bootstrap server.\n"
                      "Node ip: {}\n".format(node_ip),
                      "Node id: {}\n".format(node_id))

        self._set_default_node_parameters()

        #self._join()

    def _set_default_node_parameters(self) -> None:

        self.predecessor = None
        self.successor = None

    def set_predecessor(self, predecessor) -> None:
        self.predecessor = predecessor

    def set_successor(self, successor, set_pred=False) -> None:
        self.successor = successor

        if set_pred:
            self.set_predecessor(self.find_predecessor(self.get_node_id()))

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

    def join(self) -> None:

        """
        Performs the three steps at the join of the node.
        1. Init the finger table.
        2. Update other nodes of the join.
        3. Notify higher layer software.
        (Step 3 not implemented in the initial version.)
        :return: None
        """

        if debug:
            print("My id {}".format(self.get_node_id()))

        if debug:
            print("Starting join ....")

        if not self._bootstrap_server:
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

        else:
            try:

                nprime = xmlrpc.client.ServerProxy('http://' + self._bootstrap_server + '/RPC2')
                nprime.get_finger_table()
                self.set_predecessor(nprime.find_predecessor(self.get_node_id()))

                if debug:
                    print("My predecessor is: " + str(self.get_predecessor()))

                self.set_successor(self.get_xml_client(self.get_predecessor()).get_successor())
                    #set_successor((self.get_node_id(), self.get_connection_string()), True)

                self._init_finger_table(nprime)
                self._update_others()

                #(self.get_xml_client(self.get_predecessor())).set_successor(
                 #   (self.get_node_id(), self.get_connection_string()))

                (self.get_xml_client(self.get_successor())).set_predecessor(
                    (self.get_node_id(), self.get_connection_string()))
                (self.get_xml_client(self.get_predecessor())).set_successor(
                    (self.get_node_id(), self.get_connection_string()))

                # move keys in (predecessor, n] from successor
            except Exception as e:
                traceback.print_exc()
                print("Invalid bootstrap server provided or failed to join the p2p system.")
                exit(1)

        if debug:
            print(str(self._finger_table))

    @staticmethod
    def get_xml_client(node):
        return xmlrpc.client.ServerProxy("http://" + node[1] + "/RPC2")

    def _init_finger_table(self, bootstrap_server):

        successor = self.get_successor() #bootstrap_server.find_successor(Finger.i_start(self.get_node_id(), 1))

        # new
        self.set_predecessor(self.get_xml_client(successor).get_predecessor())
        # (self.get_xml_client(self.get_successor())).set_predecessor((self.get_node_id(), self.get_connection_string()))
        # (self.get_xml_client(self.get_predecessor())).set_successor((self.get_node_id(), self.get_connection_string()))

        if debug:
            print("Found successor {}, {}.".format(str(successor[0]), successor[1]))

        finger = Finger(ip=successor[1].split(":")[0], identifier=successor[0],
                        port=successor[1].split(":")[1], finger_number=1, my_chord_server_node_id=self.get_node_id())
        finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + successor[1] + '/RPC2'))
        finger.set_node(successor[0])
        self._finger_table.update_finger_at_ith_position(i=0, finger=finger)
        self._finger_table.get_finger_ith(0)._node = successor[0]

        self.set_successor(successor)

        for i in range(self._config.get_m_bits()-1):

            print(str(self._finger_table))

            if self.in_bracket(Finger.i_start(self.get_node_id(), i+2),
                               [self.get_node_id(), self._finger_table.get_finger_ith(i).node],
                               type='l'):
                finger = self._finger_table.get_finger_ith(i)
                new_finger = finger.create_copy(my_chord_server_id=self.get_node_id())
                new_finger.set_finger_number(i+2)
                #new_finger.set_node(self.find_successor(finger.node)[0])
                new_finger.set_node(finger.node)

                self._finger_table.update_finger_at_ith_position(i+1, new_finger)
            else:
                entry = bootstrap_server.find_successor(Finger.i_start(self.get_node_id(), i+2))
                finger = Finger(ip=entry[1].split(":")[0], identifier=entry[0],
                                finger_number=i+2, port=entry[1].split(":")[1],
                                my_chord_server_node_id=self.get_node_id())
                finger.set_node(entry[0])
                self._finger_table.update_finger_at_ith_position(i+1, finger)

    def _update_others(self):

        for i in range(self._config.get_m_bits()):
            p = self.find_predecessor(Finger.go_back_n(self.get_node_id(), 2**(i)))
            if debug:
                print("Predecessor of " + str(Finger.go_back_n(self.get_node_id(), 2**(i))) + " is : " + str(p) + ": " + str(i))
            client = xmlrpc.client.ServerProxy('http://' + p[1] + '/RPC2')
            client.update_finger_table((self.get_node_id(), self.get_connection_string()), i)

    def update_finger_table(self, s, i, for_leave=False):

        if for_leave:
            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i + 1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            return

        if self.in_bracket(s[0], [self.get_node_id(), self._finger_table.get_finger_ith(i).node], type='l'):

            if debug:
                print("Updating finger table of node {} and finger number {}.".format(self.get_node_id(),i))
                print(str(self._finger_table))

            finger = Finger(ip=s[1].split(":")[0], identifier=s[0], port=s[1].split(":")[1], finger_number=i+1,
                            my_chord_server_node_id=self.get_node_id())
            finger.set_node(s[0])
            finger.set_xml_client(xmlrpc.client.ServerProxy('http://' + s[1] + '/RPC2'))
            self._finger_table.update_finger_at_ith_position(i, finger)

            p = self.get_predecessor()

            while True:
                try:
                    if p[1] == self.get_connection_string():

                        if debug:
                            print("\n\n{} : Predecessor same as node.\n\n".format(self.get_node_id()))

                        p_client = self
                        #self.set_predecessor(p_client.find_predecessor(self.get_node_id()))
                    else:

                        if debug:
                            print("Update finger table for node id {} and finger number {}.".format(p[0], i))

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
        predecessor = self.find_predecessor(identifier)
        predecessor_client = xmlrpc.client.ServerProxy('http://' + predecessor[1] + '/RPC2')
        return predecessor_client.get_successor()

    def find_predecessor(self, identifier):

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
        m = self._config.get_m_bits()
        for i in range(m-1, -1, -1):
            if self.in_bracket(self._finger_table.get_finger_ith(i).node, [self.get_node_id(), identifier],
                               "o"):
                return self._finger_table.get_finger_ith(i).node, \
                       self._finger_table.get_finger_ith(i).get_connection_string()
        return self.get_node_id(), self.get_connection_string()

    def leave(self):

        self.get_xml_client(self.get_predecessor()).set_successor(self.get_successor())
        self.get_xml_client(self.get_successor()).set_predecessor(self.get_predecessor())
        self.get_xml_client(self.get_predecessor()).update_finger_table(self.get_successor(), 0, True)

    def in_bracket(self, num, limits, type='c'):

        if debug:
            print(num, limits[0], limits[1], type, end=' ')

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

    @staticmethod
    def belongs_to(i, x, y, x_clause='open', y_clause='close'):
        """
        Returns true if i belongs to (x,y) if x_clause = open and y_clause = open and respectively.
        :param i: node id to be checked for belongitivity
        :param x: first interval value
        :param y: second interval value
        :param x_clause: first interval closed or open (default open)
        :param y_clause: second interval closed or open (default closed)
        :return: return Boolean true or false based on condition matching
        """

        if x_clause == "open" and y_clause == "open":

            if x < i < y:
                return True

            elif i < x and i < y < x:
                return True

            return False

        if x_clause == "open" and y_clause == "close":

            if x < i <= y:
                return True

            elif i < x and i <= y < x:
                return True

            return False

        if x_clause == "close" and y_clause == "open":

            if x <= i < y:
                return True

            elif i <= x and i < y <= x:
                return True

            return False

        if x_clause == "close" and y_clause == "close":

            if x <= i <= y:
                return True

            elif i <= x and i <= y <= x:
                return True

            return False

        return False
