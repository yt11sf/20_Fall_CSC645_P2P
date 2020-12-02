# Lab: 5
# Author: <your name>
# SID: <your student id>
# Description: in this lab students will learn how to extract decoded values from a bencoded torrent file
# Implement all the methods marked as TODO

import torrent_parser as tp
import hashlib


class Torrent:

    def __init__(self, torrent_path):
        self.torrent_path = torrent_path
        self.torrent_data = tp.parse_torrent_file(torrent_path)

    def comment(self):
        """
        Already implemented for you
        This method extracts the creation_date *comment* from the torrent file
        :return: tbe comment
        """
        return self.torrent_data['comment']

    def _hash_torrent_info(self, torrent_info):
        """
        Hash the torrent info from the meta-info in the torrent file.
        :param torrent_info:
        :return: the
        """
        sha1 = hashlib.sha1()
        sha1.update(torrent_info)
        return sha1.hexdigest()

    def info_hash(self, torrent_info):
        """
        TODO: Creates the torrent info hash (SHA1) from the info section in the torrent file
              Note: must use the private method '_hash_torrent_info(...)' to hash the torrent_info
        :return: the SHA1 hash of the torrent info
        """
        return self._hash_torrent_info(torrent_info.encode('utf-8'))

    def validate_hash_info(self, info_hash):
        """
        Already implemented for you
        :param info_hash:
        :return:
        """
        return self.info_hash() == info_hash

    def announce(self):
        """
        TODO: This method extracts the announce value from the torrent file
        :return: the announce value
        """
        return self.torrent_data['announce']

    def nodes(self):
        """
        TODO: This method extracts the nodes from the torrent file
        :return: the nodes list
        """
        return self.torrent_data['info']['source']

    def creation_date(self):
        """
        TODO: This method extracts the creation_date value from the torrent file
        :return: the creation date value
        """
        return str(self.torrent_data['creation date'])

    def created_by(self):
        """
        TODO: This method extracts the created by value from the torrent file
        :return: the created by value
        """
        return self.torrent_data['created by']

    def file_name(self):
        """
        TODO: This method extracts the file_name value from the torrent file
        :return: the file name value
        """
        return self.torrent_data['info']['name']

    def file_length(self):
        """
        TODO: This method extracts the file length value from the torrent file
        :return: the length value
        """
        return str(self.torrent_data['info']['length'])

    def num_pieces(self):
        """
        TODO: This method extracts the num of pieces from the torrent file
        :return: the num of pieces
        """
        return str(len(self.torrent_data['info']['pieces']))


    def pieces(self):
        """
        TODO: This method extracts the SHA1 hashed pieces by from the torrent file
              Note: you don't need to hash the pieces. They are already hashed in the torrent file
        :return: a list of hashed pieces
        """
        pieces = "\n"
        for n in range(int(self.num_pieces())-1):
            pieces += self.piece(n) + "\n"
        return pieces

    def piece(self, index):
        """
        TODO: This method extracts a specific SHA1 hashed piece from the torrent file at the index passed as a parameter
              Note: you don't need to hash the piece. It is already hashed in the torrent file
        :param index: the index of the piece
        :return: the hashed piece
        """
        return self.torrent_data['info']['pieces'][index]

    def piece_length(self):
        """
        TODO: This method extracts the piece length from the torrent file
        :return: the piece length value
        """
        return str(self.torrent_data['info']['piece length'])

    def metainfo(self):
        """
        TODO: Create a string representing all the metainfo decoded from the torrent file
              Note: you MUST use the return of your methods to create the metainfo string
        :return: the torrent metainfo
        """
        metainfo = ""
        metainfo += "> Announce: " + self.announce() + \
                    "\n> Comment: " + self.comment() + \
                    "\n> Created by: " + self.created_by() + \
                    "\n> Creation date: " + self.creation_date() + \
                    "<< Info >>" + \
                    "\n> Length: " + self.file_length() + \
                    "\n> Name: " + self.file_name() + \
                    "\n> Piece length: " + self.piece_length() + \
                    "\n> Number of pieces: " + self.num_pieces() + \
                    "\n> Pieces: " + self.pieces() + \
                    "\n> Nodes/Source: " + self.nodes()
        metainfo += "\n> Unique torrent info hash ID: " + self.info_hash(metainfo)
        return metainfo



# uncomment the following code for testing
#
# torrent = Torrent("age.torrent")
# metainfo = torrent.metainfo()
# print(metainfo)



