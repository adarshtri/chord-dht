from utilities.config import Config
from hash.consistent_hashing import ConsistentHashing
#from chord.finger_table import FingerTable
from chord.finger import Finger
import numpy as np
from messaging.inter_class_messaging import InterClassMessaging as Messaging


class ChordNode(object):
    def __init__(self, node_id, node_ip = 'self', connector = None):
        self.config = Config()
        self.m_bits = self.config.m_bits
        self.node_id = node_id
        self.node_hash = ConsistentHashing.get_modulo_hash(node_id, self.config.m_bits)
        self.store_data = {}

        if(node_ip == 'self'):
            self.node_ip = self
        else:
            self.node_ip = node_ip

        self.finger_table = []
        self.join(connector)

    def join(self, connector = None):
        if(connector):
            self.predecessor = Messaging.send_message(connector, 'find_predecessor', id = self.node_hash)
            self.successor = self.predecessor.get_successor()
            self.init_finger_table(connector)
            self.update_others()
            self.setup_store_data()
        else:
            for i in range(self.m_bits):
                self.finger_table.append(self.new_finger(self, i))
            self.predecessor = self.new_finger(self)
            self.successor = self.new_finger(self)

    def init_finger_table(self,connector):
        self.finger_table.append(self.new_finger(self.successor, 0))
        self.predecessor = self.finger_table[0].get_predecessor()
        self.finger_table[0].set_predecessor(self.new_finger(self))
        self.predecessor.set_successor(self.new_finger(self))
        for i in range(self.m_bits - 1):
            if(self.in_bracket(self.finger_start(i+1),[self.node_hash, self.finger_table[i].node_hash],'l')):
                self.finger_table.append(self.new_finger(self.finger_table[i], i +1))
            else:
                self.finger_table.append(Messaging.send_message(connector, 'find_successor', id = self.finger_start(i+1)))

    def update_others(self, finger = 'self'):
        if(finger == 'self'):
            finger = self
        for i in range(self.m_bits):
            p = self.find_predecessor(self.node_hash - 2**(i) % 2**self.m_bits)
            Messaging.send_message(p.node_ip, 'update_finger_table', finger = self.new_finger(finger), i = i)

    def update_finger_table(self, finger, i):
        if(self.in_bracket(finger.node_hash, [self.node_hash, self.finger_table[i].node_hash],'l')):
            self.finger_table[i] = self.new_finger(finger, i)
            p = self.get_predecessor()
            Messaging.send_message(p.node_ip, 'update_finger_table', finger = finger, i = i)


    #Routines for finding predecessors and successors.
    def find_predecessor(self, id):
        n_prime = self.new_finger(self)
        while(not self.in_bracket(id, [n_prime.node_hash, n_prime.get_successor().node_hash], 'r')):
            n_prime = Messaging.send_message(n_prime.node_ip, 'closest_preceding_finger', id = id)
        return n_prime

    def find_successor(self, id):
        predecessor = self.find_predecessor(id)
        return predecessor.get_successor()

    def closest_preceding_finger(self, id):
        for i in range(self.m_bits - 1, -1, -1):
            if(self.in_bracket(self.finger_table[i].node_hash, [self.node_hash, id],'o')):
                return self.new_finger(self.finger_table[i])
        return self.new_finger(self)

    #Basic Setter and getter function
    def set_keys(self, data, path_length = 0):
        for key,value in data.items():
            key_hash = ConsistentHashing.get_modulo_hash(key, self.config.m_bits)
            predecessor = self.find_predecessor(key_hash)
            if(predecessor.node_id == self.node_id):
                self.store_data[key] = value
            else:
                Messaging.send_message(predecessor.node_ip, 'set_keys', data = {key:value})

    def get_keys(self, data):
        response = {}
        for key in data:
            key_hash = ConsistentHashing.get_modulo_hash(key, self.config.m_bits)
            predecessor = self.find_predecessor(key_hash)
            if(predecessor.node_id == self.node_id):
                response[key] = self.store_data[key]
            else:
                response[key] = Messaging.send_message(predecessor.node_ip, 'get_keys', data = [key])[key]
        return response


    #On passing data to a new node.
    def setup_store_data(self):
        data = Messaging.send_message(self.predecessor.node_ip, 'get_store_data', node_hash = self.node_hash)
        for key, value in data.items():
            self.store_data[key] = value

    def get_store_data(self, node_hash):
        data_to_transfer = {}
        to_delete = []
        for key, value in self.store_data.items():
            key_hash = ConsistentHashing.get_modulo_hash(key, self.config.m_bits)
            if(key_hash > node_hash):
                data_to_transfer[key] = value
                to_delete.append(key)

        for key in to_delete:
            del self.store_data[key]
        return data_to_transfer

    #Utility Functions
    def in_bracket(self,num,limits,type = 'c'):
        lower, higher = limits
        in_between_flag = None
        if(lower == higher):
            in_between_flag = True
        else:
            if(lower < higher):
                in_between_flag = (lower < num) and (num < higher)
            else:
                in_between_flag = not ((higher < num) and (num < lower))

        right_touch_flag = (num == lower) and not ((type == 'c') or (type == 'r'))
        left_touch_flag = (num == higher) and not ((type == 'c') or (type == 'l'))

        return in_between_flag and not(right_touch_flag or left_touch_flag)

    def relative_offset(self, requestor_id):
        requestor_hash = ConsistentHashing.get_modulo_hash(requestor_id, self.config.m_bits)
        return int(np.log2((requestor_hash - self.node_hash) % 2**self.m_bits))

    #Printing functions
    def print_finger_table(self):
        print('\nStart finger table for, ', self.node_id)
        for i in range(self.m_bits):
            print(i,self.finger_table[i].node_id, self.finger_table[i].node_hash, self.finger_table[i].start, self.finger_table[i].interval)
        print('End\n')

    def print_store_data(self):
        print('\n Start Store Data for, ', self.node_id)
        for key,value in self.store_data.items():
            print(key,value)
        print('End\n')

    def print_node_summary(self):
        print('Printing Node Summary')
        print(self.node_id, self.node_ip, self.node_hash)
        self.print_finger_table()
        self.print_store_data()
        print('\n\n\n')

    #Miscellaneous Functions

    def new_finger(self, finger, i = None):
        new_finger = Finger(node_id = finger.node_id, node_ip = finger.node_ip, node_hash = finger.node_hash)
        if(i is not None):
            new_finger.start = self.finger_start(i)
            new_finger.interval = [self.finger_start(i), self.finger_start(i+1)]
        return new_finger

    def finger_start(self, i):
        return (self.node_hash + 2**(i)) % 2**self.m_bits

    def get_successor(self):
        return self.successor

    def get_predecessor(self):
        return self.predecessor

    def set_successor(self, successor):
        self.successor = successor
        for i in range(self.relative_offset(self.successor.node_id)):
            self.finger_table[i] = self.new_finger(successor,i)

    def set_predecessor(self, predecessor):
        self.predecessor = predecessor


    #Leaving the system
    def leave(self):
        if(not self.predecessor.node_id == self.node_id):
            self.update_others(finger = self.successor)
            # print('Code was here',self.predecessor.node_id)
            # Messaging.send_message(self.predecessor.node_ip, 'set_keys', data = self.store_data)

    def __del__(self):
        self.leave()
