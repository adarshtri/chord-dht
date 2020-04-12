import socket
import threading
import socketserver
from utilities.configuration import ConfigurationManager


__all__ = ["ChordSocketServerThreadManager", "ChordSocketClient"]


class ChordSocketServerHandler(socketserver.StreamRequestHandler, socketserver.ThreadingMixIn):

    """
    This is a singleton class with not __init__ method. Can't have multiple server instances.
    The request handler our class for the dht server.
    The handle method receives a message from a client and forwards it to a handler class.
    The handler class will decide the suitable handler for the received message.
    This is a file stream based implementation where the files are used as buffers.
    """

    def handle(self):

        """
        Receives the data sent from client. Expects every data to be separated by \n.
        :return: None
        """

        data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(data)


class ThreadedChordTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ChordSocketClient(object):

    def __init__(self, host, port, message):

        self._host = host
        self._port = port
        self._message = message

    def send(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            # Connect to the server and send data
            sock.connect((self._host, self._port))

            if self._message[-1] == "\n":
                sock.sendall(bytes(self._message, "utf-8"))
            else:
                sock.sendall(bytes(self._message + "\n", "utf-8"))


class ChordSocketServerThreadManager(object):

    server = None
    server_thread = None

    @staticmethod
    def start_server():

        """
        Start the socket server to listen on the specified port.
        Sets the attribute "open_server" of the class which is used to later close the server on stop_server() method.
        :return: None
        """

        ip = ConfigurationManager.get_configuration().get_advertised_ip()
        port = ConfigurationManager.get_configuration().get_socket_port()

        if not ChordSocketServerThreadManager.server:
            ChordSocketServerThreadManager.server = \
                ThreadedChordTCPServer((ip, port), ChordSocketServerHandler)

            ChordSocketServerThreadManager.server_thread = \
                threading.Thread(target=ChordSocketServerThreadManager.server.serve_forever)

            ChordSocketServerThreadManager.server_thread.daemon = True
            ChordSocketServerThreadManager.server_thread.start()

    @staticmethod
    def stop_server():

        """
        Stops the running server for this instance.
        :return: None
        """
        if ChordSocketServerThreadManager.server and ChordSocketServerThreadManager.server_thread:
            ChordSocketServerThreadManager.server.shutdown()
            ChordSocketServerThreadManager.server.server_close()
