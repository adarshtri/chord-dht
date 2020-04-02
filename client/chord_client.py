import xmlrpc.client
import consistent_hashing


class ChordClient(object):

    def __init__(self, bootstrap_server):

        self._bootstrap_server = bootstrap_server

        try:
            self._xml_rpc_client = xmlrpc.client.ServerProxy("http://" + bootstrap_server + "/RPC2")
        except Exception as e:
            print("Are you sure you are providing correct ip:port?")
            exit(1)

    def _get_xml_rpc_client(self):
        return self._xml_rpc_client

    def store(self, key):
        return self._get_xml_rpc_client().store(key)

    def delete(self, key):
        return self._get_xml_rpc_client().delete(key)

    def get(self, key):
        return self._get_xml_rpc_client().get(key)
