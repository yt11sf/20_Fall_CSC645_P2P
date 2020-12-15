########################################################################################################################
# Class: Computer Networks
# Date: 02/03/2020
# Lab3: TCP Client Socket
# Goal: Learning Networking in Python with TCP sockets
# Student Name: Brad Patrick Peraza
# Student ID: 916768260
# Student Github Username: eraaaza
# Instructions: Read each problem carefully, and implement them correctly.  No partial credit will be given.
########################################################################################################################

# don't modify this imports.
import socket
import pickle


######################################## Client Socket ###############################################################3
"""
Client class that provides functionality to create a client socket is provided. Implement all the TODO parts 
"""

class Client(object):

    def __init__(self):
        """
        Class constructor
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = None
        self.student_name = "Brad Patrick Peraza" # TODO: your name
        self.github_username = "eraaaza" # TODO: your username
        self.sid = 916768260 # TODO: your student id

    def connect(self, server_ip_address, server_port):
        """
        TODO: Create a connection from client to server
        :param server_ip_address:
        :param server_port:
        :return:
        """
        # TODO: 1. use the self.client to create a connection with the server
        self.client.connect((server_ip_address, server_port))

        # TODO: 2. once the client creates a successful connection, the server will send the client id to this client.
        #      call the method set_client_id() to implement that functionality
        # data dictionary already created for you. Don't modify.
        self.set_client_id()

        data = {'student_name': self.student_name, 'github_username': self.github_username, 'sid': self.sid}

        #TODO  3. send the above data to the server. using the send method which has been already implemented for you.
        self.send(data)

        while True: # client is put in listening mode to retrieve data from server.
            data = self.receive()
            if not data:
                break
            # do something with the data
            self.send(data)
        self.close()

    def send(self, data):
        """
        Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data) # serialized data
        self.client.send(data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.client.recv(MAX_BUFFER_SIZE) # deserializes the data from server
        return pickle.loads(raw_data)

    def set_client_id(self):
        """
        Sets the client id assigned by the server to this client after a succesfull connection
        :return:
        """
        data = self.receive() # deserialized data
        client_id = data['clientid'] # extracts client id from data
        self.client_id = client_id # sets the client id to this client
        print("Client id " + str(self.client_id) + " assigned by server")

    def close(self):
        """
        TODO: close this client
        :return: VOID
        """
        self.client.close()


# main execution
if __name__ == '__main__':
    server_ip_address = "127.0.0.1"  # don't modify for this lab only
    server_port = 12000 # don't modify for this lab only
    client = Client()
    client.connect(server_ip_address, server_port)

# How do I know if this works?
# when this client connects, the server will assign you a client id that will be printed in the client console
# Your server must print in console all your info sent by this client
# See README file for more details


