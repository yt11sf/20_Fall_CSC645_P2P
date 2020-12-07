# File: tracker.py
# Author: Brad Patrick Peraza
# SID: 916768260
# Date: 11/6/2020
# Description: this file contains the implementation of the tracker class.

import bencodepy
import threading
from server import *  # assumes that your server file is in this folder

class Tracker:
    """
    This class contains methods that provide implementations to support trackerless peers
    supporting the DHT and KRPC protocols
    """

    DHT_PORT = 5000

    def __init__(self, server, torrent, announce=False):
        """
        TODO: Add more work here as needed.
        :param server:
        :param torrent:
        :param announce:
        """
        self._server = server
        self._torrent = torrent
        self._is_announce = announce
        #self._clienthandler = server.client_handlers[0]
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", self.DHT_PORT))
        # will story a list of dictionaries representing entries in the routing table
        # dictionaries stored here are in the following form
        # {'nodeID': '<the node id is a SHA1 hash of the ip_address and port of the server node and a random uuid>',
        #  'ip_address': '<the ip address of the node>', 'port': '<the port number of the node',
        #  'info_hash': '<the info hash from the torrent file>', last_changed': 'timestamp'}
        self._routing_table = []

    def broadcast(self, message, self_broadcast_enable=False):
        try:
            encoded_message = self.encode(message)
            self.udp_socket.sendto(encoded_message, ('<broadcast>', self.DHT_PORT))
            print("Message broadcast.....")
        except socket.error as error:
            print(error)

    def broadcast_listener(self):
        try:
            print("Listening at DHT port.....", self.DHT_PORT)
            while True:
                raw_data, sender_ip_and_port = self.udp_socket.recvfrom(4096)
                if raw_data:
                    data = self.decode(raw_data)
                    ip_sender = sender_ip_and_port[0]
                    port_sender = sender_ip_and_port[1]
                    print("Data recieved by sender", data, ip_sender, port_sender)
        except:
            print("Error listening at DHT port")

    def encode(self, message):
        """
        bencodes a message
        :param message: a dictionary representing the message
        :return: the bencoded message
        """
        return bencodepy.encode(message)

    def decode(self, bencoded_message):
        """
        Decodes a bencoded message
        :param bencoded_message: the bencoded message
        :return: the original message
        """
        return bencodepy.decode(bencoded_message)

    def ping(self, t, y, a=None, r=None):
        """
        TODO: implement the ping method
        :param t:
        :param y:
        :param a:
        :return:
        """
        """
        TODO: implement the ping method. 
        :return:
        """
        pass

    def find_node(self, t, y, a=None, r=None):
        """
        TODO: implement the find_node method
        :return:
        """
        pass

    def get_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the get_peers method
        :return:
        """
        pass

    def announce_peers(self, t, y, a=None, r=None):
        """
        TODO: implement the announce_peers method
        :return:
        """
        pass

    def process_query(self):
        """
        TODO: process an incoming query from a node
        :return: the response
        """
        pass

    def send_response(self, message, ip, port):
        """
        TODO: send a response to a specific node
        :return:
        """
        try:
            new_socket = self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
            new_socket.sendto(message, (ip, port))
        except:
            print("error")

    #Peer 2 annouce is false so does not matter
    def run(self, start_with_broadcast=False):
        """
        TODO: This function is called from the peer.py to start this tracker
        :return: VOID
        """
        if self._is_announce == True:
            threading.Thread(target=self.broadcast_listener).start()
            if start_with_broadcast:
                message = "Anyone listening in DHT port?"
                self.broadcast(message, self_broadcast_enable=True)
        else:
            print("This tracker does not support DHT protocol")