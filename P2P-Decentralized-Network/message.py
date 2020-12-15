import math
from bitarray import bitarray  # you must install this library
import unittest


class Message:
    """
    This class represents a basic implementation of the Peer Wire Protocol (PWP) used by BitTorrent protocol
    to provide reliable communication methods between peers in the same P2P network
    """

    # handshake constants
    PSTR = "BitTorrent protocol"
    PSTRLEN = 19

    # constants
    X_BITFIELD_LENGTH = b'0000'
    X_PIECE_LENGTH = b'0000'

    def __init__(self, peer_id, info_hash):
        # A keep-alive message must be sent to maintain the connection alive if no command
        # have been sent for a given amount of time. This amount of time is generally two minutes.
        self.keep_alive = {'len': b'0000'}

        # The uploader cannot upload more data to the swarm. Causes could be congestion control..
        self.choke = {'len': b'0001', 'id': 0}

        # The uploader is ready to upload more data to the swarm.
        self.unchoke = {'len': b'0001', 'id': 1}

        # The downloader is interested in downloading data from the requested peer.
        self.interested = {'len': b'0001', 'id': 2}

        # The downloader is not interested in downloading data from the requested peer.
        self.not_interested = {'len': b'0001', 'id': 3}

        # The payload is a piece that has been successfully downloaded and verified via the hash.
        self.have = {'len': b'0005', 'id': 4, 'piece_index': None}

        # The payload is a bitfield representing the pieces that have been successfully downloaded.
        # The high bit in the first byte corresponds to piece index 0.
        # Bits that are cleared indicated a missing piece, and set bits indicate a valid and available piece.
        # Spare bits at the end are set to zero.
        # [[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1]]
        self._bitfield = {'len': b'0013' +
                          self.X_BITFIELD_LENGTH, 'id': 5, 'bitfield': []}
        # The request message is fixed length, and is used to request a block.
        # The payload contains the following information:
        #     index: integer specifying the zero-based piece index
        #     begin: integer specifying the zero-based byte offset within the piece
        #     length: integer specifying the requested length.
        self.request = {'len': b'0013', 'id': 6,
                        'index': None, 'begin': None, 'length': None}

        # The piece message is variable length, where X is the length of the block.
        # The payload contains the following information:
        #     index: integer specifying the zero-based piece index
        #     begin: integer specifying the zero-based byte offset within the piece
        #     block: block of data, which is a subset of the piece specified by index.
        self.piece = {'len': b'0009' + self.X_PIECE_LENGTH,
                      'id': 7, 'index': None, 'begin': None, 'block': None}

        # The payload is identical to that of the "request" message. It is typically used during "End Game"
        # The "End Game"
        self.cancel = {'len': b'0013', 'id': 8,
                       'index': None, 'begin': None, 'length': None}

        # The port message is sent by newer versions of the Mainline that implements a DHT tracker.
        # The listen port is the port this peer's DHT node is listening on.
        # This peer should be inserted in the local routing table (if DHT tracker is supported).
        self.port = {'index': b'0003', 'id': 9, 'listen-port': None}

        # The handshake message
        # This message is the first message sent to a peer once trackers from both peers shared the DHT, and there is
        # a reliable connection active.
        # the handshake message contains the following data:
        #     info_hash
        #            Note: Must be bencoded first
        #            The 20 byte sha1 hash of the bencoded form of the info value from the metainfo file.
        #            This value will almost certainly have to be escaped.
        #            Note that this is a substring of the metainfo file. The info-hash must be the hash of the encoded
        #            form as found in the .torrent file, which is identical to bdecoding the metainfo file, extracting
        #            the info dictionary and encoding it if and only if the bdecoder fully validated the input
        #            (e.g. key ordering, absence of leading zeros). Conversely that
        #            means clients must either reject invalid metainfo files or extract the substring directly.
        #            They must not perform a decode-encode roundtrip on invalid data.
        #      peer_id
        #            Each peer generates its own id at random at the start of a new download. This value will also
        #            almost certainly have to be escaped.
        #            A good peer_id can be created by using a SHA1 hash of the concatenation of the following values:
        #                 (1) unique uuid id
        #                 (2) ip address
        #                 (3) port
        #      pstr
        #            The protocol used for this message. By default is ""BitTorrent protocol"
        #      pstrlen
        #            The len of the message. Assuming we use the default pstr in the handshake message, then the
        #            default value for pstr is 19
        #
        self.handshake = {'info_hash': info_hash, 'peer_id': peer_id,
                          'pstr': self.PSTR, 'pstrlen': self.PSTRLEN}

        #  Tracker requests have the following keys:
        #      info_hash
        #            The 20 byte sha1 hash of the bencoded form of the info value from the metainfo file.
        #            This value will almost certainly have to be escaped.
        #            Note that this is a substring of the metainfo file. The info-hash must be the hash of the encoded
        #            form as found in the .torrent file, which is identical to bdecoding the metainfo file, extracting
        #            the info dictionary and encoding it if and only if the bdecoder fully validated the input
        #            (e.g. key ordering, absence of leading zeros). Conversely that
        #            means clients must either reject invalid metainfo files or extract the substring directly.
        #            They must not perform a decode-encode roundtrip on invalid data.
        #      peer_id
        #            Each peer generates its own id at random at the start of a new download. This value will also
        #            almost certainly have to be escaped.
        #            A good peer_id can be created by using a SHA1 hash of the concatenation of the following values:
        #               (1) unique uuid id
        #               (2) ip address
        #               (3) port
        #      ip
        #            An optional parameter giving the IP (or dns name) which this peer is at. Generally used for the
        #            origin if it's on the same machine as the tracker.
        #      port
        #            The port number this peer is listening on. Common behavior is for a downloader to try to listen
        #            on port 6881 and if that port is taken try 6882, then 6883, etc. and give up after 6889.
        #      uploaded
        #            The total amount uploaded so far, encoded in base ten ascii.
        #      downloaded
        #            The total amount downloaded so far, encoded in base ten ascii.
        #      left
        #            The number of bytes this peer still has to download, encoded in base ten ascii. Note that this
        #            can't be computed from downloaded and the file length since it might be a resume, and there's a
        #            chance that some of the downloaded data failed an integrity check and had to be re-downloaded.
        #      event
        #            This is an optional key which maps to started, completed, or stopped (or empty, which is the
        #            same as not being present). If not present, this is one of the announcements done at regular
        #            intervals. An announcement using started is sent when a download first begins, and one using
        #            completed is sent when the download is complete. No completed is sent if the file was complete
        #            when started. Downloader send an announcement using stopped when they cease downloading.
        #
        #      IMPORTANT: This message is only used when KRPC protocol is not supported by the tracker. See lab 6 for more
        #                 info about KRPC protocol
        #
        self.tracker = {'torrent_info_hash': info_hash, 'peer_id': peer_id, "ip": -1, 'port': -1, 'uploaded': -1,
                        'downloaded': -1, 'left': -1, 'event': -1}

    #############################  Bitfield Methods ####################################################

    def init_bitfield(self, num_pieces):
        """
        TODO: Initializes the bitfield with all the pieces set to missing: b'00000000'
        NOTE: Initialization of the bitarry must be in bytes. You can use the
        library bitarray to create pieces like this: bitarray(8)
        :param num_pieces: the number of pieces defined in the .torrent file
        :return: Void
        """
        size_bitfield = math.ceil(num_pieces / 8)
        spare_bits = (8 * size_bitfield) - num_pieces
        # self._bitfield['bitfield'] = [[0, 0, 0, 0, 0, 0, 0, 0], [
        #    1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]]
        # print(self._bitfield)

        for i in range(size_bitfield - 1):
            # create a bitarray (piece) of 8 bits size
            # set all the bits to 0 (missing piece)
            # add the new piece to the bitfield (self._bitfield['bitfield])
            p = bitarray(8)
            p.setall(False)
            self._bitfield['bitfield'].append(p)

        # create a new bitarray (piece) of spare bits size
        # # set all the bits to 0 (missing piece)
        # add the new piece to the bitfield (self._bitfield['bitfield])
        s = bitarray(spare_bits)
        s.setall(False)
        self._bitfield['bitfield'].append(s)
        # print(self._bitfield)

    def get_bitfield(self):
        """
        TODO: get the bitfield payload
        :return: the bitfield payload
        """
        return self._bitfield['bitfield']

    def get_bitfield_piece(self, piece_index):
        """
        TODO: gets a piece from the bitfield
        :param piece_index:
        :return: the piece bitfield located at index 'piece_index'
        """
        return self._bitfield['bitfield'][piece_index]

    def get_bitfield_block(self, piece_index, block_index):
        """
        TODO: gets a block from the bitfield
        :param piece_index:
        :param block_index:
        :return: the block bit located at index 'block_index'
        """
        return self._bitfield['bitfield'][piece_index][block_index]

    def is_block_missing(self, piece_index, block_index):
        """
        TODO: determines if a block is missing (missing blocks are set to bit 0)
        :param piece_index:
        :param block_index:
        :return: True if the block is missing. Otherwise, returns False
        """
        return False if self._bitfield['bitfield'][piece_index][block_index] else True

    def is_piece_missing(self, piece_index):
        """
        TODO: determines if a piece is missing (missing pieces has at least one block set to bit 0)
        :param piece_index:
        :return: True if the piece is missing. Otherwise, returns False
        """
        for b in self._bitfield['bitfield'][piece_index]:
            if b == 0:
                return True
        return False

    def next_missing_block_index(self, piece_index):
        """
        TODO: finds the next missing block
        :param piece_index:
        :return: the next missing block index
        """
        i = 0
        for b in self._bitfield['bitfield'][piece_index]:
            if b == 0:
                return i
            i += 1
        return -1

    def next_missing_piece_index(self):
        """
        TODO: finds the next missing piece
        :return: the next missing piece index
        """
        i = 0
        for p in self._bitfield['bitfield']:
            if self.is_piece_missing(i):
                return i
            i += 1
        return -1

    def set_block_to_completed(self, piece_index, block_index):
        """
        TODO: set the block represented by the piece_index and block_index to b'1' or True
        :param piece_index:
        :param block_index:
        :return: VOID
        """
        self._bitfield['bitfield'][piece_index][block_index] = b'1'

    def get_tracker_with_ip_port(self, ip, port):
        '''
        Retrieve tracker with ip and port set
        This was created because message instance is shared between multiple instances
        '''
        self.tracker["ip"] = ip
        self.tracker["port"] = port
        return self.tracker
