from hash.consistent_hashing import ConsistentHashing
from messaging.inter_class_messaging import InterClassMessaging as Messaging

class Finger(object):
    def __init__(self, start = None, interval = None, node_id = None, node_ip = None, node_hash = None):
        
        self.start = start
        self.interval = interval

        self.node_id = node_id
        self.node_ip  = node_ip
        self.node_hash = node_hash

    def get_successor(self):
        return Messaging.send_message(self.node_ip, 'get_successor')

    def get_predecessor(self):
        return Messaging.send_message(self.node_ip, 'get_predecessor')

    def set_successor(self, successor):
        return Messaging.send_message(self.node_ip, 'set_successor', successor = successor)

    def set_predecessor(self, predecessor):
        return Messaging.send_message(self.node_ip, 'set_predecessor', predecessor = predecessor)