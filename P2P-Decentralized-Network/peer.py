from server import Server  # assumes that your Tracker file is in this folder
from client import Client
from message import Message
from tracker import Tracker  # assumes that your Tracker file is in this folder
from torrent import Torrent  # assumes that your Torrent file is in this folder

from threading import Thread
import time
import uuid


class Peer:
    SERVER_PORT = 4998
    CLIENT_MIN_PORT_RANGE = 5001
    CLIENT_MAX_PORT_RANGE = 5010

    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000

    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    TORRENT_PATH = 'age.torrent'
    ERROR_TEMPLATE = "\033[1m\033[91mEXCEPTION in peer.py {0}:\033[0m {1} occurred.\nArguments:\n{2!r}"

    # Seeder, announce=F, role=seeder, port=5000
    # Leecher, announce=T, role=peer, port=4998
    def __init__(self, role=PEER, server_ip_address='127.0.0.1'):
        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """
        self.torrent = Torrent(self.TORRENT_PATH)
        self.message = Message(self.id, self.torrent.create_info_hash())
        self.server = Server(message=self.message,
                             server_ip_address=server_ip_address,
                             server_port=self.SERVER_PORT)
        self.server_ip_address = server_ip_address
        self.id = uuid.uuid4()  # creates unique id for the peer
        self.role = role
        # Commented out from this lab b/c not needed
        self.DHT = None
        self.tracker = self.run_tracker(True)

    def get_DHT(self):
        return self.DHT

    def run_server(self):
        """
        Starts a threaded server
        :return: VOID
        """
        try:
            # must thread the server, otherwise it will block the main thread
            Thread(target=self.server.run, daemon=False).start()
            print("Server started.........")
        except Exception as ex:
            print(self.ERROR_TEMPLATE.format(
                "run_server()", type(ex).__name__, ex.args))

    def run_tracker(self, announce=True):
        """
        Starts a threaded tracker
        :param announce: True if this is the first announce in this network
        :return: VOID
        """
        try:
            if self.server:
                self.tracker = Tracker(self.server, self.torrent, announce)
                Thread(target=self.tracker.run, daemon=False).start()
                while not self.DHT:
                    self.DHT = self.tracker.get_DHT()
                    time.sleep(.5)  # optional
                    # print("Tracker running.....")
                print("Tracker running.....")
        except Exception as ex:
            print(self.ERROR_TEMPLATE.format(
                "run_tracker()", type(ex).__name__, ex.args))

    def _connect_to_peer(self, client_port_to_bind, peer_ip_address, peer_port):
        """
        TODO: * Create a new client object and bind the port given as a
              parameter to that specific client. Then use this client
              to connect to the peer (server) listening in the ip
              address provided as a parameter
              * Thread the client
              * Run the downloader
        :param client_port_to_bind: the port to bind to a specific client
        :param peer_ip_address: the peer ip address that
                                the client needs to connect to
        :return: VOID
        """
        print('Trying ', peer_ip_address, '/', client_port_to_bind)
        client = Client(id=self.id, message=self.message)
        try:
            client.bind('0.0.0.0', client_port_to_bind)
            # must thread the client too, otherwise it will block the main thread
            Thread(target=client.connect, args=(
                peer_ip_address, peer_port)).start()
            print("Server started.........")
            return True
            # ! Need to run downloader
            # ! Either create a run method in client, or do it here
        except Exception as ex:
            print(self.ERROR_TEMPLATE.format(
                "_connect_to_peer()", type(ex).__name__, ex.args))
            client.close()
            return False

    def connect(self, peers_ip_addresses):
        """
        TODO: Initialize a temporal variable to the min client port range, then
              For each peer ip address, call the method _connect_to_peer()
              method, and then increment the client´s port range that
              needs to be bind to the next client. Break the loop when the
              port value is greater than the max client port range.
        :param peers: list of peer´s ip addresses in the network
        :return: VOID
        """
        client_port = self.CLIENT_MIN_PORT_RANGE
        for ip_address in peers_ip_addresses:
            if client_port > self.CLIENT_MAX_PORT_RANGE:
                print("Connected max Peer ports...")
                break
            if '/' in peer_ip:
                peer_ip, peer_port = peer_ip.split('/')
            if self._connect_to_peer(client_port, peer_ip, int(peer_port)):
                client_port += 1


if __name__ == '__main__':
    role = input('Enter role: ') or 'peer'  # ! testing
    server_ip_address = input('Enter peer port: ') or '127.0.0.1'  # ! testing
    # testing
    peer = Peer(role=role, server_ip_address=server_ip_address)

    # testing #seeder for server. peer for leecher
    print("Peer: " + str(peer.id) + " running its server: ")
    peer.run_server()
    # print("Peer: " + str(peer.id) + " running its clients: ")
    # Two ways of testing this:
    #  Locally (same machine):
    #      1. Run two peers in the same machine using different ports. Comment out the next three lines (only servers run)
    #      2. Then run a third peer, executing the next two lines of code.
    #  Using different machines
    #      1. Run two peers in different machines.
    #      2. Run a peer in this machine.

    # if peer.role == peer.LEECHER or peer.role == peer.PEER:
    if peer.role == peer.SEEDER:
        # this list will be sent by the tracker in your P2P assignment
        peer_ips = peer.get_DHT()
        peer.connect(peer_ips)

     """ Sample output running this in the same machine """
    # Peer: 6d223864-9cd7-4327-ad02-7856d636af66 running its server:
    # Listening for new peers at 127.0.0.1/5000
    # Peer: 6d223864-9cd7-4327-ad02-7856d636af66 running its clients:
    # Client id 5001 connected to peer 127.0.0.1/7001
    # Client id 5002 connected to peer 127.0.0.1/7000

    """ Sample output running one peer in this machibe in the other two in different machines """
    # Peer: 6f4e024e9-0265-47ba-a525-1c880a7a9a5d running its server:
    # Listening for new peers at 10.0.0.248/5000
    # Peer: f4e024e9-0265-47ba-a525-1c880a7a9a5d running its clients:
    # Client id 5001 connected to peer 10.0.0.251/5000
    # Client id 5002 connected to peer 127.0.0.242/5000
