import xmlrpc.client


class ChordClient(object):

    """
    Author: Adarsh Trivedi
    This class provides basic methods a client can perform on a chord network (get/set/delete).
    """

    def __init__(self, bootstrap_server):
        """
        Author: Adarsh Trivedi
        :param bootstrap_server: Server used to connect to the p2p network.
        """
        self._bootstrap_server = bootstrap_server

        try:
            self._xml_rpc_client = xmlrpc.client.ServerProxy("http://" + bootstrap_server + "/RPC2")
        except Exception as e:
            print("Are you sure you are providing correct ip:port?")
            exit(1)

    def _get_xml_rpc_client(self):
        return self._xml_rpc_client

    def set(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        :param key: Key to be stored on network.
        :param hash_it: Whether to perform hashing on key or not.
        :return: Node on which key was store.
        """
        return self._get_xml_rpc_client().set(key, hash_it)

    def delete(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        :param key: Key to be delete from network.
        :param hash_it: Whether to perform hashing on key or not.
        :return: Node from which key was deleted.
        """
        return self._get_xml_rpc_client().delete(key, hash_it)

    def get(self, key, hash_it=True):
        """
        Author: Adarsh Trivedi
        :param key: Key to be retrieved from the network.
        :param hash_it: Whether to perform hashing on key or not.
        :return: Node from which key was retrieved.
        """
        return self._get_xml_rpc_client().get(key, hash_it)
