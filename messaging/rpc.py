from xmlrpc import server
import threading
import socketserver
from utilities.configuration import ConfigurationManager


class Node(object):

    def __init__(self, z):
        self.z = z

    def add(self, x, y):
        return x+y+self.z


class ChordRPCRequestHandler(server.SimpleXMLRPCRequestHandler):
    rpc_paths = ('/', '/RPC2',)


class AsyncXMLRPCServer(socketserver.ThreadingMixIn, server.SimpleXMLRPCServer):
    pass


class XMLRPCChordServerManager(object):

    server = None
    server_thread = None

    @staticmethod
    def start_server():

        ip = ConfigurationManager.get_configuration().get_advertised_ip()
        port = ConfigurationManager.get_configuration().get_socket_port()

        if not XMLRPCChordServerManager.server and not XMLRPCChordServerManager.server_thread:
            XMLRPCChordServerManager.server = AsyncXMLRPCServer((ip, port), ChordRPCRequestHandler)
            XMLRPCChordServerManager.server.register_instance(Node(z=10))
            XMLRPCChordServerManager.server_thread = \
                threading.Thread(target=XMLRPCChordServerManager.server.serve_forever)
            XMLRPCChordServerManager.server_thread.daemon = True
            XMLRPCChordServerManager.server_thread.start()

    @staticmethod
    def stop_server():

        if XMLRPCChordServerManager.server and XMLRPCChordServerManager.server_thread:
            XMLRPCChordServerManager.server.shutdown()
            XMLRPCChordServerManager.server.server_close()
