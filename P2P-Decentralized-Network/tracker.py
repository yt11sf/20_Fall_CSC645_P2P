from server import Server

from collections import OrderedDict
import socket
import threading
import bencodepy


class Tracker:
    DHT_PORT = 6000
    SELF_PORT = 6000  # Change port for other peers

    ERROR_TEMPLATE = "\033[1m\033[91mEXCEPTION in tracker.py {0}:\033[0m {1} occurred.\nArguments:\n{2!r}"

    def __init__(self, server, torrent, announce):
        self.server = server
        self.torrent = torrent
        self.announce = announce
        if self.announce:
            self.SELF_PORT = 12006
        self.torrent_info_hash = self._get_torrent_info_hash()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(("", self.SELF_PORT))
        # will story a list of dictionaries representing entries in the routing table
        # dictionaries stored here are in the following form
        # {'nodeID': '<the node id is a SHA1 hash of the ip_address and port of the server node and a random uuid>',
        #  'ip_address': '<the ip address of the node>', 'port': '<the port number of the node',
        #  'info_hash': '<the info hash from the torrent file>', last_changed': 'timestamp'}
        self._routing_table = []

    def _get_torrent_info_hash(self):
        """
        creates the torrent info hash (SHA1) from the info section in the torrent file
        """
        return self.torrent.create_info_hash()

    def add_peer_to_swarm(self, peer_id, peer_ip, peer_port):
        """
        TODO: when a peers connects to the network adds this peer
              to the list of peers connected
        :param peer_id:
        :param peer_ip:
        :param peer_port:
        :return:
        """
        pass  # your code here

    def remove_peer_from_swarm(self, peer_id):
        """
        TODO: removes a peer from the swarm when it disconnects from the network
              Note: this method needs to handle exceptions when the peer disconnected abruptly without
              notifying the network (i.e internet connection dropped...)
        :param peer_id:
        :return:
        """
        pass  # your code here

    def broadcast(self, message, self_broadcast_enabled=False):
        try:
            encoded_message = self.encode(message)
            self.udp_socket.sendto(
                encoded_message, ('<broadcast>', self.DHT_PORT))
            print("Message broadcast.....")
        except socket.error as error:
            print(error)

    def send_udp_message(self, message, ip, port):
        try:
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self.encode(message)
            new_socket.sendto(message, (ip, port))
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
                    print("data received by sender",
                          data, ip_sender, port_sender)
                    if not self.announce:
                        self.process_query(data, ip_sender, port_sender)
                    else:
                        self._routing_table = data
                    exit(1)

        except Exception as ex:
            print(self.ERROR_TEMPLATE.format(
                "broadcast_listerner()", type(ex).__name__, ex.args))

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
            # r = {"id": self.encode(self._server.host)}
            if self.torrent.validate_hash_info(self.decode(data["a"]["id"])):
                # Harcode ip address to be localhost for testing
                # self._routing_table = [str(ip_sender) + "/" + str(port_sender)]
                self._routing_table = [
                    "127.0.0.1" + "/" + str(self.server.server_port)]
                print("Hashed info data matches!...")
                self.send_udp_message(self._routing_table, ip_sender, port_sender)


    def get_DHT(self):
        return self._routing_table

    def encode(self, message):
        # bencodes a message
        return bencodepy.encode(message)

    def decode(self, bencoded_message):
        # decodes a bencode message
        bc = bencodepy.Bencode(encoding='utf-8')
        return bc.decode(bencoded_message)

    def set_total_uploaded(self, peer_id):
        """
        TODO: sets the total data uploaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def total_downloaded(self, peer_id):
        """
        TODO: sets the total data downloaded so far by the peer passed as a parameter
        :param peer_id:
        :return: VOID
        """
        pass  # your code here

    def validate_torrent_info_hash(self, peer_torrent_info_hash):
        """
        TODO: compare the info_hash generated by this peer with another info_hash sent by another peer
              this is done to make sure that both peers agree to share the same file.
        :param peer_torrent_info_hash: the info_hash from the info section of the torrent sent by other peer
        :return: True if the info_hashes are equal. Otherwise, returns false.
        """
        if self.torrent.validate_hash_info(peer_torrent_info_hash):
            return True
        return False

    def ping(self, t, y, q, a=None):
        # create the ping dictionary
        a = {"id": self.encode(self.torrent.create_info_hash())}
        ping_query = {"t": t, "y": y, "q": q, "a": a}
        # pass the dictionary
        self.broadcast(ping_query, self_broadcast_enabled=True)
        # self.process_response()

    def run(self):  # mod if start with broad casr
        """
        TODO: This function is called from the peer.py to start this tracker
        :return: VOID
        """
        if self.announce:
            print("Broadcasting to DHT Port: ", self.DHT_PORT)
            self.ping("aa", "q", "ping")
            self.broadcast_listerner()
        else:
            threading.Thread(target=self.broadcast_listerner).start()
