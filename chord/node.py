from utilities.configuration import ConfigurationManager


class Finger(object):

    """
    Represent every entry in the finger table of the node.
    Contains basic attributes like ip, key(identifier) and port.
    """

    def __init__(self, ip, identifier, port):
        self._ip = ip
        self._identifier = identifier
        self._port = port

    def __str__(self):
        return "| {} | {} | {} |\n".format(self._ip, self._identifier, self._port)


class FingerTable(object):

    """
    Represents the finger table for each node. Encapsulates some helper functions
    for the finger table.
    """

    def __init__(self, size):
        self._table_size = size
        self._table = []

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

    def __str__(self):

        s = "Finger Table\n"
        s += "| IP | Identifier | Port |\n"
        for finger in self._table:
            s += str(finger)
        return s


class Node(object):

    def __init__(self, node_id, node_ip, bootstrap_node=None):

        self._node_id = node_id
        self._node_ip = node_ip
        self._bootstrap_server = bootstrap_node
        self._config = ConfigurationManager.get_configuration()
        self._finger_table = FingerTable(size=self._config.get_m_bits())
        self._join()

    def _join(self) -> None:

        """
        Performs the three steps at the join of the node.
        1. Init the finger table.
        2. Update other nodes of the join.
        3. Notify higher layer software.
        (Step 3 not implemented in the initial version.)
        :return: None
        """

        if not self._bootstrap_server:
            for i in range(1, self._config.get_m_bits()+1):
                finger = Finger(ip=self._config.get_chord_server_ip(),
                                identifier=self._node_id,
                                port=self._config.get_socket_port())
                self._finger_table.append_new_finger(finger)
            print(self._finger_table)
        else:
            self._init_finger_table(self._bootstrap_server)
            self._update_others()
            # move keys in (predecessor, n] from successor

    def _init_finger_table(self, bootstrap_server):
        pass

    def _update_others(self):
        pass

    def get_finger_table(self):
        return str(self._finger_table)
