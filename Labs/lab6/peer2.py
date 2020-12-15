"""
Lab 6: peer.py
This file contains a basic template of the Peer class.
"""

from server import *  # assumes that your server file is in this folder
from client import *  # assumes that your client file is in this folder
from tracker2 import *  # assumes that your Tracker file is in this folder
from torrent import *  # assumes that your Torrent file is in this folder
from threading import Thread
import uuid


class Peer:
    """
    In this part of the peer class we implement methods to connect to multiple peers.
    Once the connection is created downloading data is done in similar way as in TCP assigment.
    """
    SERVER_PORT = 5000
    CLIENT_MIN_PORT_RANGE = 5001


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
        self.torrent = Torrent("age.torrent")
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

    def run_client(self):
        try:
            Thread(target=self.client.connect(), daemon=False).start()
            print("Client running.....")
        except Exception as error:
            print(error)

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
                print("Tracker running.....")
        except Exception as error:
            print(error)  # server failed to run


# runs when executing python3 peer.py
# main execution
if __name__ == '__main__':
    # testing
    peer = Peer(role='peer')
    print("Peer: " + str(peer.id) + "started....")
    #peer.run_server()
    #peer.run_client()
    peer.run_tracker()