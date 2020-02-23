import socket
import threading
import socketserver
from constants.messaging_constants import MessagingConstants


__all__ = ["ChordSocketServerThreadManager", "ChordSocketClient"]


class ChordSocketServer(socketserver.StreamRequestHandler):

    open_server = None

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

    @staticmethod
    def start_server():

        """
        Start the socket server to listen on the specified port.
        Sets the attribute "open_server" of the class which is used to later close the server on stop_server() method.
        :return:
        """
        if not ChordSocketServer.open_server:
            with socketserver.TCPServer((MessagingConstants.SERVER_HOST, MessagingConstants.SERVER_PORT), ChordSocketServer) as server:
                ChordSocketServer.open_server = server
                server.serve_forever()

    @staticmethod
    def stop_server():

        """
        Stops the running server for this instance.
        :return: None
        """
        if ChordSocketServer.open_server:
            ChordSocketServer.open_server.server_close()


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

    server_thread = None

    @staticmethod
    def start_socket_server():

        if not ChordSocketServerThreadManager.server_thread:
            ChordSocketServerThreadManager.server_thread = threading.Thread(target=ChordSocketServer.start_server, args=())
            ChordSocketServerThreadManager.server_thread.start()

    @staticmethod
    def stop_socket_server():

        if ChordSocketServerThreadManager.server_thread:
            ChordSocketServer.stop_server()
            ChordSocketServerThreadManager.server_thread.join()
