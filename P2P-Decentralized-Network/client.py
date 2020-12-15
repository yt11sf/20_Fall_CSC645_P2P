import socket
import pickle

from downloader import Downloader
from custom_exception import ClientClosedException, ProtocolException


class Client(object):
    """
    The client class provides the following functionality:
    1. Connects to a TCP server
    2. Send serialized data to the server by requests
    3. Retrieves and deserialize data from a TCP server
    """

    ERROR_TEMPLATE = "\033[1m\033[91mEXCEPTION in client.py {0}:\033[0m {1} occurred.\nArguments:\n{2!r}"

    def __init__(self, peer_id, torrent, message):
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_id = 0
        self.peer_id = peer_id
        self.torrent = torrent
        # first true is for interested, second is for keep alive
        self.download = Downloader(
            self.clientSocket, self.peer_id, self.torrent, True, True)
        self.message = message

    def set_info(self):
        self._send(self.message.handshake)
        data = self._receive()
        if self.handle_response(data) == 'status-ok':
            pass
        print('Your client info is:')
        print("Client ID: " + str(self.client_id))

    def connect(self, host="127.0.0.1", port=12005):
        """
        TODO: Connects to a server. Implements exception handler if connection is resetted. 
            Then retrieves the cliend id assigned from server, and sets
        :param host: 
        :param port: 
        :return: VOID
        """
        try:
            self.clientSocket.connect((host, port))
            print(f'Successfully connected to server: %s/%d' % (host, port))
            self.set_info()
            # client is put in listening mode to retrieve data from server.
            while True:
                try:
                    #    print('waiting for server')
                    data = self._receive()
                    if not data:
                        break
                    #    print(data)
                    response = self.handle_response(data)
                    # if there is a response
                    if response:
                        self._send(response)
                except ClientClosedException as ex:
                    print(
                        '\n--------------------Client Disconnected---------------------\n')
                    break
                except ProtocolException as ex:
                    print(self.ERROR_TEMPLATE.format(
                        "connect()", type(ex).__name__, ex.args))
                except:
                    raise
        except socket.error as ex:
            print(self.ERROR_TEMPLATE.format(
                "connect()", type(ex).__name__, ex.args))
        except Exception as ex:
            print(self.ERROR_TEMPLATE.format(
                "connect()", type(ex).__name__, ex.args))
        self.close()

    def handle_response(self, data):
        """
        This function handle the client's action according to the protocols send by the server
        :param: deserialized server response
        :return: raw client response
        """
        #    print(data)
        response = {}
        # self-defined protocol in TCP project
        if 'headers' in data:
            # going through all the data
            for header in data['headers']:
                # if printing message
                if header['type'] == 'print':
                    self.print_message(header['body'])
                # if getting input
                elif header['type'] == 'input':
                    response[header['body']['res-key']
                             ] = self.get_input(header['body'])
                # return status
                elif header['type'] == 'ignore':
                    response = 'ignore'
                # if closing connection
                elif header['type'] == 'close':
                    response['client-closed'] = True
                    self._send(response)
                    raise ClientClosedException()
                elif header['type'] == 'status-ok':
                    return 'status-ok'
                else:
                    print(self.ERROR_TEMPLATE.format(
                        "handle_response()", "ProtocolException", f"Header is wrong: %s" % header))
                    raise ProtocolException(
                        'Protocol received from server is invalid')
            if response:
                if response != 'ignore':
                    return response
            else:
                return {'status': 'ok'}
        # Bitorrent protocol
        else:
            pass

    def print_message(self, body):
        """
        This function simply print the message from the server
        :param: protocol's body
        """
        message = body['message']
        print(message)

    def get_input(self, body):
        """
        This function get the client response according to the server protocols
        :param: protocol's body
        :return: client response body
        """
        while True:
            try:
                message = body['message']
                data_type = body['res-type']
                data = input(message)
                if data_type == 'string':
                    data = str(data)
                elif data_type == 'int':
                    data = int(data)
                break
            except:
                print('\n--->Client Input Invalid<---\n')
        return data

    def _send(self, data):
        """
        Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data)  # serialized data
        self.clientSocket._send(data)

    def _receive(self, MAX_BUFFER_SIZE=4090):
        """
        Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.clientSocket.recv(MAX_BUFFER_SIZE)
        return pickle.loads(raw_data)

    def close(self):
        """
        TODO: close the client socket
        :return: VOID
        """
        self.clientSocket.close()


if __name__ == '__main__':
    host = input('Enter the server IP Address: ') or "127.0.0.1"
    port = input('Enter the server port: ') or 12005
    client = Client()
    client.connect(host, int(port))
