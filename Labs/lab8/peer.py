"""
Lab 8: peer.py
This file contains a basic template of the Peer class. In this lab, your job
is to implement all the parts marked as TODO.
Note that you don´t need to run the code of this lab. The goal of this lab is to see how your logic works, and
therefore, to make sure that you understood how peers perform the downloading
and uploading process in the network, and also which challenges you may encounter
when implementing those functionality.
"""
from server import Server  # assumes that your server file is in this folder
from client import Client  # assumes that your client file is in this folder
from tracker import Tracker  # assumes that your Tracker file is in this folder
from torrent import Torrent  # assumes that your Torrent file is in this folder
import uuid
from threading import Thread


class Peer:
    SERVER_PORT = 5000
    CLIENT_MIN_PORT_RANGE = 5001
    CLIENT_MAX_PORT_RANGE = 5010

    MAX_NUM_CONNECTIONS = 10
    MAX_UPLOAD_RATE = 100
    MAX_DOWNLOAD_RATE = 1000

    PEER = 'peer'
    LEECHER = 'leecher'
    SEEDER = 'seeder'

    def __init__(self, role=SEEDER, server_ip_address='127.0.0.1'):
        """
        Class constructor
        :param server_ip_address: used when need to use the ip assigned by LAN
        """
        self.server = Server(server_ip_address, self.SERVER_PORT)  # inherits methods from the server
        self.server_ip_address = server_ip_address
        self.id = uuid.uuid4()  # creates unique id for the peer
        self.role = role
        self.torrent = Torrent()
        self.tracker = None

    def run_server(self):
        """
        Starts a threaded server
        :return: VOID
        """
        try:
            # must thread the server, otherwise it will block the main thread
            Thread(target=self.server.run, daemon=False).start()
            print("Server started.........")
        except Exception as error:
            print(error)  # server failed to run

    #def run_tracker(self, announce=True):
        """
        Starts a threaded tracker
        :param announce: True if this is the first announce in this network
        :return: VOID
        """
        #try:
            #if self.server:
                #self.tracker = Tracker(self.server, self.torrent, announce)
                #Thread(target=self.tracker.run, daemon=False).start()
                #print("Tracker running.....")
        #except Exception as error:
            #print(error)  # server failed to run

    def _connect_to_peer(self, client_port_to_bind, peer_ip_address, peer_port=5000):
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
        client = Client()
        try:
            client.bind('0.0.0.0', client_port_to_bind)  # your code here
            Thread(target=client.connect_to_server, args=(peer_ip_address, peer_port)).start()
            return True
        except Exception as error:
            print(error)  # handle exceptions here
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
        client_port = self.CLIENT_MIN_PORT_RANGE  # your code here
        default_peer_port = self.SERVER_PORT
        for peer_ip in peers_ip_addresses:
            if client_port > self.CLIENT_MAX_PORT_RANGE:
                break
            if "/" in peer_ip:
                ip_and_port = peer_ip.split("/")
                peer_ip = ip_and_port[0]
                default_peer_port = int(ip_and_port[1])
            if self._connect_to_peer(client_port,peer_ip,default_peer_port):
                client_port += 1


# testing
peer = Peer(role='peer')
print("Peer: " + str(peer.id) + " running its server: ")
peer.run_server()
#print("Peer: " + str(peer.id) + " running its clients: ")
# Two ways of testing this:
#  Locally (same machine):
#      1. Run two peers in the same machine using different ports. Comment out the next three lines (only servers run)
#      2. Then run a third peer, executing the next two lines of code.
#  Using different machines
#      1. Run two peers in different machines.
#      2. Run a peer in this machine.
if peer.role == peer.LEECHER or peer.role == peer.PEER:
    peer_ips = ['127.0.0.1/4998', '127.0.0.1/4999']  # this list will be sent by the tracker in your P2P assignment
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
