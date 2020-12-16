# File: tracker.py
# Author: YeeJian Tan
# SID: 920115752
# Date: 11/03/20
# Description: this file contains the implementation of the tracker class.

from collections import OrderedDict
from threading import Thread
import bencodepy
import socket
import time


class Tracker:
    """
    This class contains methods that provide implementations to support trackerless peers
    supporting the DHT and KRPC protocols
    """
    DHT_PORT = 12001
    MAX_BUFFERSIZE = 4096

    def __init__(self, server, torrent, announce=True, DHT_PORT=12001):
        """
        TODO: Add more work here as needed.
        :param server:
        :param torrent:
        :param announce:
        """
        self._server = server
        self._torrent = torrent
        self._is_announce = announce
        # self._clienthandler = server.clienthandlers[0]
        self.id = None
        self.ip_address = None
        self.DHT_PORT = DHT_PORT
        self.udpsocket = None
        self._set_udpsocket()
        '''        
        # will story a list of dictionaries representing entries in the routing table
        # dictionaries stored here are in the following form
        # {'nodeID': '<the node id is a SHA1 hash of the ip_address and port of the server node and a random uuid>',
        #  'ip_address': '<the ip address of the node>', 'port': '<the port number of the node',
        #  'info_hash': '<the info hash from the torrent file>', last_changed': 'timestamp'}
        '''
        # ! response_time is only measured one way: send request -> receive request
        # {info_hash: [(response_time, (ip_address, port))]}
        self._routing_table = {}
        # explored nodes in routing table to prevent further exploration
        # [(ip_address, port)]
        self.explored_nodes = []
        # expected number of response before announce peer
        self.exp_num_of_res = 0
        self.token = ''

    def get_DHT(self):
        return self._routing_table

    def _set_udpsocket(self):
        self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udpsocket.bind(('', self.DHT_PORT))
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.id = {
            "uuid": "aaaa",
            "ip_address": self.ip_address,
            "port": self.DHT_PORT,
            "info_hash": self._torrent.create_info_hash()
        }

    def broadcast(self, message, broadcast_enable=False):
        try:
            print('Broadcasting message from',
                  socket.gethostbyname(socket.gethostname()), ': ', message)
            encoded_message = self.encode(message)
            self.udpsocket.sendto(
                encoded_message, ('<broadcast>', self.DHT_PORT))
        except Exception as ex:
            print('Tracker broadcast error')
            print(ex)

    def broadcast_listener(self):
        try:
            print('Listening at DHT port: ', self.DHT_PORT)
            while True:
                raw_data, sender_ip_port = self.udpsocket.recvfrom(
                    self.MAX_BUFFERSIZE)
                if raw_data:
                    data = self.decode(raw_data)
                    # ! close VPN
                    # print(socket.gethostbyname(socket.gethostname()))
                    # print(sender_ip_port)
                    if sender_ip_port[0] != self.ip_address:
                        print(f'Received data from %s: %s' %
                              (sender_ip_port, data))
                        # processing query
                        # this is suppose to only handle query that is broadcasted
                        # which is ping only?
                        self.process_all(data)

                    # ! Debug self message
                    else:
                        print('The sender receive its own message: ', data)
                else:
                    break
        except Exception as ex:
            print('Tracker broadcast listener error')
            print(ex)

    def encode(self, message):
        """
        bencodes a message
        :param message: a dictionary representing the message
        :return: the bencoded message
        """
        return bencodepy.encode(message)

    def decode(self, bencoded_data):
        """
        Decodes a bencoded data
        :param bencoded_data: the bencoded message
        :return: decoded_data
        """
        decoded_data = self._decode_utf8(bencodepy.decode(bencoded_data))
        return decoded_data

    def _decode_utf8(self, encoded_data):
        """
        Decodes a utf-8 encoded data
        :param encoded_data: the encoded message
        :return: decoded_data
        """
        try:
            if type(encoded_data) == bytes:
                return encoded_data.decode('utf-8')
            elif type(encoded_data) == OrderedDict:
                decoded_dict = {}
                for k, v in encoded_data.items():
                    decoded_dict[self._decode_utf8(k)] = self._decode_utf8(v)
                return decoded_dict
            elif type(encoded_data) == str:
                return encoded_data
            elif type(encoded_data) == int:
                return encoded_data
            elif type(encoded_data) == tuple:
                if len(encoded_data) == 1:
                    return self._decode_utf8(encoded_data[0])
                else:
                    print('ERROR --> Tuple length != 1')
                    raise Exception()
            else:
                print('ERROR --> Unknown type')
                raise Exception()
        except Exception as ex:
            print('_decode_utf8 unsuccessful: ', encoded_data)
            print(ex)

    def _generate_tokens(self, ip_address):
        '''
        Create a sha1 hash from ip_address
        '''
        return "token"  # ! hardcode for now

    def _add_node(self, info_hash, response_time, ip_address_port):
        '''
        Append a node into routing table
        :param info_hash: sha1 hash of torrent's info_hash
        :param ip_address_port: tuple of node's ip address and port
        :param response_time: response time of node
        '''
        if info_hash in self._routing_table:
            self._routing_table[info_hash].append(
                (response_time, ip_address_port))
        else:
            self._routing_table[info_hash] = [(response_time, ip_address_port)]

    def _get_sender_addr(self, data):
        '''
        Getting the sender ip_address and port from data
        :return: tuple of ip_address and port
        '''
        return (data['a']['id']['ip_address'],
                data['a']['id']['port'])

    def ping(self, t):
        """
        TODO: implement the ping method
        :param t: transaction id
        """
        '''
            ping Query = {"t":"aa", "y":"q", "q":"ping", "a":{
                "id":"abcdefghij0123456789"}}
            bencoded = d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:
                t2:aa1:y1:qe
        '''
        data = {
            "t": t,
            "y": "q",
            "q": "ping",
            "a": {"id": self.id},
            "time": time.time()
        }
        self.broadcast(data)

    def _response_ping(self, t, sender_time, sender_addr):
        """
        Response ping request
        :param t: data
        """
        '''
            Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
            bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
        '''
        response = {
            "t": t,
            "y": "r",
            "q": "ping",  # tell receiver this is a response of ping
            "r":  {"id": self.id},
            "res_time": time.time() - sender_time
        }
        self.send_response(response, sender_addr)

    def find_node(self, t, target_info_hash):
        """
        TODO: implement the find_node method
        :param t: transaction id
        :param target_id: target
        :param target_info_hash: target's info hash
        """
        self._routing_table[target_info_hash] = []
        data = {
            "t": t,
            "y": "q",
            "q": "find_node",
            "a": {
                "id": self.id,
                "target": target_info_hash
            },
            "time": time.time()
        }
        self.send_response(data)

    def _response_find_node(self, t, target_info_hash, sender_time, sender_addr):
        '''
        Response a find_node request if self info_hash == target_info_hash
        :param t: transaction id
        :param target_info_hash: target's info hash
        '''
        if self.id['info_hash'] == target_info_hash:
            data = {
                "t": t,
                "y": "r",
                "q": "find_node",
                "r": {"id": self.id},
                "res_time": time.time() - sender_time
            }
            self.send_response(data, sender_addr)

    def get_peers(self, t, sender_addr):
        """
        TODO: implement the get_peers method
        :param t: transaction id
        :param sender_addr: (ip_address, port)
        """
        '''
            get_peers Query = {"t":"aa", "y":"q", "q":"get_peers",
                "a": {"id":"abcdefghij0123456789", "info_hash":"mnopqrstuvwxyz123456"}}
            bencoded = d1:ad2:id20:abcdefghij01234567899:
                info_hash20:mnopqrstuvwxyz123456e1:q9:get_peers1:t2:aa1:y1:qe
        '''
        data = {
            "t": t,
            "y": "q",
            "q": "get_peers",
            "a": {"id": self.id},
            "time": time.time()
        }
        self.send_response(data, sender_addr)

    def _response_get_peers(self, t, info_hash, sender_time, sender_addr):
        '''
        Response to get_peers request
        :param t: transaction id
        :param sender_addr: (ip_address, port)
        '''
        '''
            Response with peers = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", 
                "token":"aoeusnth", "values": ["axje.u", "idhtnm"]}}
            bencoded = d1:rd2:id20:abcdefghij01234567895:token8:
                aoeusnth6:valuesl6:axje.u6:idhtnmee1:t2:aa1:y1:re

            Response with closest nodes = {"t":"aa", "y":"r", "r": {
                "id":"abcdefghij0123456789", "token":"aoeusnth", "nodes": "def456..."}}
            bencoded = d1:rd2:id20:abcdefghij01234567895:
                nodes9:def456...5:token8:aoeusnthe1:t2:aa1:y1:re
        '''
        values = self._routing_table[info_hash][1] \
            if info_hash in self._routing_table else []
        data = {
            "t": t,
            "y": "r",
            "q": "get_peers",
            "r": {
                "id": self.id,
                # ! hardcode for now
                "token": self._generate_tokens(sender_addr[0]),
                "values": values,
            },
            "res_time": time.time() - sender_time
        }
        self.send_response(data, sender_addr)

    def announce_peers(self, t, implied_port, port, token, sender_addr):
        """
        TODO: implement the announce_peers method
        :param t: transaction id
        :param implied_port: if ignore port and use source port of the UDP packet
        :param port: port to download file
        :param token: token
        :param sender_addr: (ip_address, port)
        """
        '''
            announce_peers Query = {"t":"aa", "y":"q", "q":"announce_peer", "a": {
                "id":"abcdefghij0123456789", "implied_port": 1, 
                "info_hash":"mnopqrstuvwxyz123456", "port": 6881, "token": "aoeusnth"}}
            bencoded = d1:ad2:id20:abcdefghij012345678912:implied_porti1e9:info_hash20:
                mnopqrstuvwxyz1234564:porti6881e5:token8:aoeusnthe1:q13:announce_peer1:
                t2:aa1:y1:qe
        '''
        data = {
            "t": t,
            "y": "q",
            "q": "announce_peer",
            "a": {
                "id": self.id,
                "implied_port": implied_port,
                "port": port,
                "token": token
            },
            "time": time.time()
        }
        self.send_response(data, sender_addr)

    def _response_announce_peers(self, t, sender_time, sender_addr):
        """
        Response to announce_peers request
        :param t: transaction id
        :param sender_addr: (ip_address, port)
        """
        '''
            Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
            bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
        '''
        data = {
            "t": t,
            "y": "r",
            "q": "announce_peer",
            "r": {
                "id": self.id,
            },
            "res_time": sender_time - time.time()
        }
        self.send_response(data, sender_addr)

    def process_all(self, data):
        '''
        Process all communication coming through
        '''
        if data['y'] == 'q':
            self.process_query(data)
        elif data['y'] == 'r':
            self.process_response(data)
        elif data['y'] == 'e':
            print('Response Error')

    def process_query(self, data):
        """
        TODO: process an incoming query from a node
        :return: the response
        """
        sender_addr = self._get_sender_addr(data)
        if data['q'] == 'ping':
            self._add_node(data['a']['id']['info_hash'],
                           time.time()-data['time'],
                           sender_addr)
            self._response_ping(data['t'],
                                data['time'],
                                sender_addr)
        elif data['q'] == 'find_node':
            self._response_find_node(data['t'],
                                     data['a']['id']['info_hash'],
                                     data['time'],
                                     sender_addr)
        elif data['q'] == 'get_peers':
            self._response_get_peers(data['t'],
                                     data['a']['id']['info_hash'],
                                     data['time'],
                                     sender_addr)
        elif data['q'] == 'announce_peers':
            self._response_announce_peers(data['t'],
                                          data['time'],
                                          sender_addr)

    def process_response(self, data):
        '''
        Process response from nodes
        '''
        sender_addr = self._get_sender_addr(data)
        if data['q'] == 'ping':
            self._add_node(data['r']['id']['info_hash'],
                           data['res_time'],
                           sender_addr)
            self.get_peers(data['t'], sender_addr)
        elif data['q'] == 'find_node':
            self.exp_num_of_res -= 1
            # select the 8 fastest response to add to routing table
            # if less than 8 nodes, add node
            if len(self._routing_table['info_hash']) < 8:
                self._add_node(self.id['info_hash'],
                               data['res_time'],
                               sender_addr)
            else:
                # select the node that take the most time to response
                max_res_time_node = max(
                    self._routing_table['info_hash'], key=lambda v: v[0])
                # if that node take more time than this node
                if max_res_time_node[0] > data['res_time']:
                    # remove that node and add this node
                    self._routing_table['info_hash'].remove(max_res_time_node)
                    self._add_node(data['r']['id']['info_hash'],
                                   data['res_time'],
                                   sender_addr)
            # if every get_peers response has been processed
            if self.exp_num_of_res == 0:
                # announce_peer to every node remained in routing table
                for _, node in self._routing_table['info_hash']:
                    # ! hardcoded for now, use UDP port
                    self.announce_peers(
                        data['t'], 1, self.DHT_PORT, self.token, node)
        elif data['q'] == 'get_peers':
            self.token = data['r']['token']
            # for every node in get_peers response
            for v in data['r']['values']:
                # if it is not already explored
                if v not in self.explored_nodes:
                    # record it and send find_node request
                    self.explored_nodes.append(v)
                    self.exp_num_of_res += 1
                    self.find_node(data['t'], self.id['info_hash'])
        elif data['q'] == 'announce_peers':
            print('received announce peer response')

    def send_response(self, data, sender_addr):
        """
        TODO: send a response to a specific node
        :return:
        """
        try:
            print('Send response from ', socket.gethostbyname(socket.gethostname()),
                  ' to ', sender_addr, ': ', data)
            encoded_data = self.encode(data)
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            new_socket.sendto(encoded_data, sender_addr)
            new_socket.close()
        except Exception as ex:
            print('Tracker send_response errror')
            print(ex)

    def run(self, start_w_broadcast=True):
        """
        TODO: This function is called from the peer.py to start this tracker
        :return: VOID
        """
        if self._is_announce:
            Thread(target=self.broadcast_listener).start()
            if start_w_broadcast:
                self.ping('aa')  # ! hard code transaction id
        else:
            print('This tracker does not support DHT protocol')


if __name__ == '__main__':
    from torrent import *
    torrent = Torrent('age.torrent')
    tracker = Tracker(None, torrent)
    tracker.run()
