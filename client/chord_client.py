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

    def set(self, key, hash_it=True):
        return self._get_xml_rpc_client().set(key, hash_it)

    def delete(self, key, hash_it=True):
        return self._get_xml_rpc_client().delete(key, hash_it)

    def get(self, key, hash_it=True):
        return self._get_xml_rpc_client().get(key, hash_it)
