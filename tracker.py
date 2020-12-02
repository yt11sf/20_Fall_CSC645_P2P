# File: tracker.py for Peer 1
# Author: Kevin Nunura
# SID: 920347620
# Date: 11/11/2020
# Description: this file contains the implementation of the tracker class.

import bencodepy
import socket
import threading

class Tracker:
    """
    This class contains methods that provide implementations to support trackerless peers
    supporting the DHT and KRPC protocols
    """
    DHT_PORT = 6000

    def __init__(self, server, client, torrent, announce=True):
        """
        TODO: Add more work here as needed.
        :param server:
        :param torrent:
        :param announce:
        """
        self._server = server
        self._client = client
        self._torrent = torrent
        self._is_announce = announce
        # self._clienthandler = server.clienthandlers[0]
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", self.DHT_PORT))
        self.non_broadcast_socket = None
        # will story a list of dictionaries representing entries in the routing table
        # dictionaries stored here are in the following form
        # {'nodeID': '<the node id is a SHA1 hash of the ip_address and port of the server node and a random uuid>',
        #  'ip_address': '<the ip address of the node>', 'port': '<the port number of the node',
        #  'info_hash': '<the info hash from the torrent file>', last_changed': 'timestamp'}
        self.DHT_routing_table = None

    def broadcast(self, message, self_broadcast_enabled=False):
        try:
            encoded_message = self.encode(message)
            self.udp_socket.sendto(encoded_message, ('<broadcast>', self.DHT_PORT))
            # print("Message broadcast.....")
        except socket.error as error:
            print(error)

    def send_udp_message(self, message, target_ip, target_port):
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
            new_socket.sendto(message, (target_ip, 12006)) #HARDCODING port 12006 for communication with Peer 3 because else it wont work
        except:
            print("error")

    def broadcast_listerner(self):
        try:
            print("Listening at DHT port: ", self.DHT_PORT)
            while True:
                raw_data, sender_ip_and_port = self.udp_socket.recvfrom(4096)
                if raw_data:
                    data = self.decode(raw_data)
                    ip_sender = sender_ip_and_port[0]
                    port_sender = sender_ip_and_port[1]
                    # print("data received by sender", data, ip_sender, port_sender)
                    self.process_query(data, ip_sender, port_sender)
        except:
            print("Error listening at DHT port")

    def process_query(self, data, ip_sender, port_sender):
        """
        TODO: process an incoming query from a node
        :return: the response
        """
        query = data.get("q")
        r = None

        # Response = {"t": "aa", "y": "r", "r": {"id": "mnopqrstuvwxyz123456"}}
        if query == "ping":
            print("ping Query: \n" + str(data) + "\n")
            r = {"id": self.encode(self._server.host)}
            if self._torrent.validate_hash_info(self.decode(data["a"]["id"])):
                self.DHT_routing_table = [{"nodeID": self._torrent.info_hash("127.0.0.1:6000"),
                                   "ip_address": "127.0.0.1",
                                   "port": self.DHT_PORT,
                                   "info_hash": self._torrent.info_hash(self._torrent.metainfo())}]

        # Response with peers = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "values": ["axje.u", "idhtnm"]}}
        # Response with closest nodes = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "nodes": "def456..."}}
        elif query == "get_peers":
            print("get_peers Query: \n" + str(data) + "\n")
            if self.DHT_routing_table:
                r = {"id": self.encode(self._server.host), "token": "aoeusnth", "values": ("["+self.DHT_routing_table[0].get("nodeID")+"]")}

        # Response = {"t": "aa", "y": "r", "r": {"id": "0123456789abcdefghij", "nodes": "def456..."}}
        elif query == "find_node":
            print("find_node Query: \n" + str(data) + "\n")
            r = {"id": self.encode(self._server.host), "nodes": self.encode(self.DHT_routing_table[0].get("nodeID"))}

        # Response = {"t": "aa", "y": "r", "r": {"id": "mnopqrstuvwxyz123456"}}
        elif query == "announce_peers":
            print("announce_peers Query: \n" + str(data) + "\n")
            r = {"id": self.encode(self._server.host)}

        response = {"t": "aa", "y": "r", "r": r}
        self.send_udp_message(response, ip_sender, port_sender)

    def encode(self, message):
        # bencodes a message
        return bencodepy.encode(message)

    def decode(self, bencoded_message):
        # decodes a bencode message
        bc = bencodepy.Bencode(encoding='utf-8')
        return bc.decode(bencoded_message)

    def ping(self, t, y, q, a=None):
        # create the ping dictionary
        a = {"id": self.encode(self._torrent.info_hash(self._torrent.metainfo()))}
        ping_query = {"t": t, "y": y, "q": q, "a": a}
        # pass the dictionary
        self.broadcast(ping_query, self_broadcast_enabled=True)
        self.process_response()

    def find_node(self, t, y, q, a=None):
        # find_node Query = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":"abcdefghij0123456789", "target":"mnopqrstuvwxyz123456"}}
        a = {"id": self.encode("127.0.0.1"), "target": self.encode("127.0.0.1:6000")}
        find_node_query = {"t": t, "y": y, "q": q, "a": a}
        self.send_udp_message(find_node_query, self._DHT_routing_table["nodes"]["ip_address"], self._DHT_routing_table["nodes"]["port"])
        self.process_response()

    def get_peers(self, t, y, q, a=None):
        # get_peers Query = {"t": "aa", "y": "q", "q": "get_peers", "a": {"id": "abcdefghij0123456789", "info_hash": "mnopqrstuvwxyz123456"}}
        a = {"id": self.encode("127.0.0.1"), "info_hash": self.encode(self._torrent.info_hash(self._torrent.metainfo()))}
        get_peers_query = {"t": t, "y": y, "q": q, "a": a}
        self.send_udp_message(get_peers_query, self._DHT_routing_table["nodes"]["ip_address"], self._DHT_routing_table["nodes"]["port"])
        self.process_response()

    def announce_peers(self, t, y, q, a=None):
        implied = 1
        a = {"id": self.encode("127.0.0.1"), "implied_port": implied, "info_hash": self._torrent.info_hash(self._torrent.metainfo()), "port": self.DHT_PORT
             , "token": "aoeusnth"}
        get_peers_query = {"t": t, "y": y, "q": q, "a": a}
        self.send_udp_message(get_peers_query, self._DHT_routing_table["nodes"]["ip_address"], self._DHT_routing_table["nodes"]["port"])
        self.process_response()


    def run(self, start_with_broadcast=False):
        """
        TODO: This function is called from the peer.py to start this tracker
        :return: VOID
        """
        if self._is_announce:
            if start_with_broadcast:
                message = "Anyone listening in DHT port?"
                self.broadcast(message, self_broadcast_enabled=True)
            else:
                threading.Thread(target=self.broadcast_listerner).start()
        else:
            print("This tracker does not support DHT protocol")
