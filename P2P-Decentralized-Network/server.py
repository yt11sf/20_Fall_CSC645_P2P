import socket
import pickle
import threading

from message import Message
from torrent import Torrent
from uploader import Uploader
from custom_exception import ProtocolException


class Server(object):
    """
    The server class implements a server socket that can handle multiple client connections.
    It is really important to handle any exceptions that may occur because other clients
    are using the server too, and they may be unaware of the exceptions occurring. So, the
    server must not be stopped when a exception occurs. A proper message needs to be show in the
    server console.
    """
    MAX_NUM_CONN = 10  # keeps 10 clients in queue
    TORRENT_PATH = 'age.torrent'
    ERROR_TEMPLATE = "\033[1m\033[91mEXCEPTION in server.py {0}:\033[0m {1} occurred.\nArguments:\n{2!r}"

    def __init__(self, server_ip_address="127.0.0.1", server_port=12000):
        """
        Class constructor
        :param server_ip_address: by default localhost. Note that '0.0.0.0' takes LAN ip address.
        :param server_port: by default 12000
        """
        self.server_ip_address = server_ip_address
        self.server_port = server_port
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clienthandlers = {}  # a list of uploaders
        self.threadStarted = {}  # DEBUGGING ONLY. keeping track of thread started
        self.lock = threading.Lock()
        self.torrent = Torrent(self.TORRENT_PATH)
        self.message = Message(-1, self.torrent.create_info_hash())

    def _bind(self):
        """
        # TODO: bind host and server_port to this server socket
        :return: VOID
        """
        self.serversocket.bind((self.server_ip_address, self.server_port))

    def _listen(self):
        """
        # TODO: puts the server in listening mode.
        # TODO: if succesful, print the message "Server listening at ip/port"
        :return: VOID
        """
        try:
            self._bind()
            self.serversocket.listen(self.MAX_NUM_CONN)
            with self.lock:
                print('Server listening at ',
                      self.server_ip_address, '/', self.server_port)
        except socket.error as ex:
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "_listen()", type(ex).__name__, ex.args))
            self.serversocket.close()
        except Exception as ex:
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "_listen()", type(ex).__name__, ex.args))
                print("The threads")
            self.serversocket.close()

    def _accept_clients(self):
        """
        #TODO: Handle client connections to the server
        :return: VOID
        """
        while True:
            try:
                # accepting client
                clientsocket, addr = self.serversocket.accept()
                # starting client thread
                self.threadStarted[addr[1]] = threading.Thread(target=self.client_handler_thread,
                                                               args=(clientsocket, addr))
                self.threadStarted[addr[1]].start()
            except socket.error as ex:
                with self.lock:
                    print(self.ERROR_TEMPLATE.format(
                        "_accept_clients()", type(ex).__name__, ex.args))
                    print("TLDR: Socket error")
                self.serversocket.close()
            except Exception as ex:
                with self.lock:
                    print(self.ERROR_TEMPLATE.format(
                        "_accept_clients()", type(ex).__name__, ex.args))
                    print("The threads")
                self.serversocket.close()

    def client_handler_thread(self, clientsocket, addr):
        """
        Sends the client id assigned to this clientsocket and
        Creates a new ClientHandler object
        See also ClientHandler Class
        :param clientsocket:
        :param address:
        :return: a client handler object.
        """
        peer_id = self.set_client_info(self, clientsocket)
        if peer_id == -1:
            with self.lock:
                print(
                    'Connection attempted but failed due to not_interested/choke/different info hash')
            return

        client_handler = Uploader(
            peer_id, self, clientsocket, addr, self.torrent)
        return client_handler

    def set_client_info(self, clientsocket):
        """
        Communicate with downloader to determine whether connection is neccessary
        :param clientsocket:
        :return:
        """
        handshake = self._receive(clientsocket)
        # {'info_hash', 'peer_id','pstr', 'pstrlen'}
        info_hash = handshake['info_hash']
        peer_id = handshake['peer_id']
        # info hash is different
        if not self.torrent.validate_hash_info(info_hash):
            self._send(clientsocket, {'status': 'not ok',
                                      'message': 'different info hash'})
            raise Exception('Received different info_hash')
        self._send(clientsocket, {'status': 'ok'})
        interested = self._receive(clientsocket)
        # interested? {'len': b'0001', 'id': 2} : {'len': b'0001', 'id': 3}
        if interested['id'] == 2:
            # too many parallel connection
            if len(self.clienthandlers) >= self.MAX_NUM_CONN:
                self._send(clientsocket, self.message.choke)
                return -1
            else:
                self._send(clientsocket, self.message.unchoke)
                return peer_id
        elif interested['id'] == 3:
            return -1
        else:   # message invalid
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "set_client_info()", "ProtocolException",
                    "Expecting interested/not_insterested from downloader but received" + str(interested)))
            raise ProtocolException(
                'Protocol received from downloader is invalid')

    def _send(self, clientsocket, data):
        """
        TODO: Serializes the data with pickle, and sends using the accepted client socket.
        :param data:
        :return:
        """
        try:
            serialized_data = pickle.dumps(data)
            clientsocket.send(serialized_data)
        except socket.error as ex:
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "_send()", type(ex).__name__, ex.args))
                print("TLDR: Socket error")
                self.serversocket.close()
        except Exception as ex:
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "_send()", type(ex).__name__, ex.args))

    def _receive(self, clientsocket, MAX_BUFFER_SIZE=4096):
        """
        TODO: Deserializes the data with pickle
        :param clientsocket:
        :param MAX_BUFFER_SIZE:
        :return: the deserialized data
        """
        try:
            # print('_receive: ' + str(pickle.loads(data)))
            data = clientsocket.recv(MAX_BUFFER_SIZE)
            return pickle.loads(data)
        except Exception as ex:
            with self.lock:
                print(self.ERROR_TEMPLATE.format(
                    "_receive()", type(ex).__name__, ex.args))

    def run(self):
        """
        Already implemented for you
        Run the server.
        :return: VOID
        """
        self._listen()
        self._accept_clients()


# main execution
if __name__ == '__main__':
    server = Server()
    server.run()
