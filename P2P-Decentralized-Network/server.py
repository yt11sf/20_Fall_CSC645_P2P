#######################################################################
# File:             server.py
# Author:           Kevin Nunura and Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template server class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this client class, and add yours instead.
# Running:          Python 2: python server.py
#                   Python 3: python3 server.py
#                   Note: Must run the server before the client.
########################################################################
# from builtins import object
import socket
import pickle
from uploader import Uploader
from threading import Thread


class Server(object):
    MAX_NUM_CONN = 10

    def __init__(self, host, port, peer_id, torrent):
        self.peer_id = peer_id
        self.torrent = torrent
        # create an INET, STREAMing socket
        self.host = host
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_handlers = {}  # dictionary of clients handlers objects handling clients. format {clientid:client_handler_object}
        # TODO: bind the socket to a public host, and a well-known port
        self.serverSocket.bind((self.host, self.port))

    def _listen(self):
        try:
            self.serverSocket.listen(self.MAX_NUM_CONN)
            print("Listening at port " + self.host + "/" + str(self.port))
        except:
            print("Server could not _listen(). Closing connection.")
            self.serverSocket.close()

    def _accept_clients(self):
        while True:
            try:
                clienthandler, addr = self.serverSocket.accept()
                thread = Thread(target=self.client_handler_thread, args=(clienthandler, addr), daemon=True)
                thread.start()
            except:
                print("Could not _accept_clients(). Closing connection.")
                self.serverSocket.close()

    def send(self, clientsocket, data):
        serialized_data_from_client = pickle.dumps(data)  # serialized data
        clientsocket.send(serialized_data_from_client)

    def receive(self, clientsocket, MAX_BUFFER_SIZE=4096):
        serialized_data_from_client = clientsocket.recv(MAX_BUFFER_SIZE)
        return pickle.loads(serialized_data_from_client)  # returns deserialized data from client

    def send_client_id(self, clientsocket, clientid):
        clientid_deserializd = {'clientid': clientid}
        self.send(clientsocket, clientid_deserializd)  # send() serializes data before sending

    def client_handler_thread(self, clientsocket, address):
        client_id = address[1]
        self.send_client_id(clientsocket, client_id)  # clientsocket comes from clienthandler in _accept_clients()
        upload = Uploader(self.peer_id, self, clientsocket, address, self.torrent)
        return upload

    def get_clients(self):
        return self.client_handlers

    def run(self):
        self._listen()
        self._accept_clients()

# if __name__ == '__main__':
#     server = Server()
#     server.run()

