from messaging.socket_messaging import ChordSocketClient, MessagingConstants

client = ChordSocketClient(host=MessagingConstants.SERVER_HOST, port=MessagingConstants.SERVER_PORT, message="Hi")
client.send()
