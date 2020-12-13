#######################################################################
# File:             client.py
# Author:           Kevin Nunura and Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template client class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this client class, and add yours instead.
# Running:          Python 2: python client.py
#                   Python 3: python3 client.py
#
########################################################################
import socket
import pickle
from downloader import Downloader
# from client_helper import ClientHelper


class Client(object):
    """
    The client class provides the following functionality:
    1. Connects to a TCP server
    2. Send serialized data to the server by requests
    3. Retrieves and deserialize data from a TCP server
    """

    def __init__(self, peer_id, torrent):
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = 0
        self.client_name = None
        self.peer_id = peer_id
        self.torrent = torrent
        #first true is for interested, second is for keep alive
        self.download = Downloader(self.clientSocket, self.peer_id, self.torrent, True, True)

    def get_client_id(self):
        return self.client_id

    def set_client_id(self):
        data = self.receive()  # deserialized data
        client_id = data['clientid']  # extracts client id from data
        self.client_id = client_id  # sets the client id to this client
        # print("Successfully connected to server: " + self.server_ip_address + "/" + str(self.server_port))
        # print("Your client info is:\nClient Name: " + self.client_name + "\nClient ID: " + str(self.client_id) + "\n")
        print("Client id " + str(self.client_id) + " connected to peer " + self.server_ip_address + "/" + str(self.server_port))

    def connect(self, peer_ip_address, peer_port):
        # self.server_ip_address = input("Enter the server IP Address: ")
        # self.server_port = int(input("Enter the server port: "))
        # self.client_name = input("Your id key (i.e your name): ")
        self.server_ip_address = peer_ip_address
        self.server_port = peer_port


        self.clientSocket.connect((self.server_ip_address, self.server_port))
        self.set_client_id()
        data = {'clientid': self.client_id}
        self.send(data)

        while True:  # client is put in listening mode to retrieve data from server.
            data = self.receive()
            if not data:
                break
            # do something with the data

        self.close()

    # def run_helper(self):
    #     client_id = self.receive()  # get rid of first message to use menu from now on
    #     client_helper = ClientHelper(self)
    #     client_helper.run()

    def send(self, data):
        data = pickle.dumps(data)  # serializes the data
        self.clientSocket.send(data)

    def receive(self, MAX_BUFFER_SIZE=4096):
        raw_data = self.clientSocket.recv(MAX_BUFFER_SIZE)
        return pickle.loads(raw_data)  # deserializes the data from server

    def close(self):
        self.clientSocket.close()

    def bind(self, ip, client_port_to_bind):
        # TODO: bind the socket to a public host, and a well-known port
        self.clientSocket.bind((ip, client_port_to_bind))

# if __name__ == '__main__':
#     server_ip_address = None
#     server_port = 0
#     client = Client()
#     client.connect()
