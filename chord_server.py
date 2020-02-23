from messaging.socket_messaging import ChordSocketServerThreadManager


def start_chord_node():
    ChordSocketServerThreadManager.start_socket_server()
