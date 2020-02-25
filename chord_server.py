from messaging.socket_messaging import ChordSocketServerThreadManager


def start_chord_node():
    ChordSocketServerThreadManager.start_server()


def stop_chord_node():
    ChordSocketServerThreadManager.stop_server()


if __name__ == "__main__":

    start_chord_node()

    while True:
        console_input = input("Enter \"stop\" to shutdown chord node: ")
        if console_input.strip() == "stop":
            stop_chord_node()
            break
