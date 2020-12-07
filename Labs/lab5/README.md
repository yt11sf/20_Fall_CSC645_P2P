# Lab #5: Getting Started with peer-to-peer Networks (P2P)
In this lab, you'll learn the basics of peer-to-peer (P2P) networks. This is a starting point in order to understand the
requirements for your next project in this class; a P2P decentralized network

## What is a P2P Network?

So far, all the labs were focused on client-server network architectures. Although the real internet works mostly
under that concept, many network engineers still think that peer-to-peer networks are the way to go to build 
the network architecture of the future internet because those networks will be decentralized, limiting the internet 
control of governments and big companies. Think about it, would a company like facebook exist in a internet 
ruled by a P2P architecture? Probably it wouldn't because host would have total control over the content they 
share. 

In a P2P network, all the peers are clients and servers at the same time. There are two main types of P2P 
architectures; semi-centralized, and decentralized architectures. 

* In a semi-decentralized P2P architecture there is still a server but it has minimal impact in the network. For 
example, providing minimal services such as list of ip addresses connected to the network. This server is
also know as tracker. 

* In a decentralized P2P architecture there are no servers as we know them. All the peers are servers and 
clients at the same time. 

## P2P Reliable Transport Protocols

In a P2P network, like in a client-server one, we need reliable transport protocols. Most of those protocols 
are build on top of TCP. In a client-server architecture HTTP is built on top of TCP. In a P2P architecture 
we can also use HTTP in some way. However, the most used protocol in P2P is the BitTorrent protocol. This 
protocol implement services that are specifically designed to handle reliable transport of data between peers
such as the BitTorrent Message Protocol (more about this in lab #7)


## P2P Entities Definitions BitTorrent Protocol Based
In a P2P network there are many protocols used to provide services. One of the most used is tha BitTorrent 
protocol. All the entities in a P2P network are well defined and have a specific job to do in the network. The following 
is a list of those entities and their definitions. 

### Seeders 
Seeders are those who uploaded the torrent seeds to others, or those who downloaded the the file already. 
### Peers 
Peers are those who are uploading and downloading data at the same time from other peers. Note that 
they do not posses the whole resource that is being shared, only some pieces of it. Peers become seeders 
for a specific file when they downloaded all the pieces from that file. 
### Leeches 
Leeches are peers that do not have the required piece of a file. For example, if there are zero seeders
in the network at some point most of the peers will become leeches. 
### Swarm
A swarm is a network of peers, leeches and seeders sharing the same file. The more seeders a swarm has, there will be 
faster downloads rates among peers. In other words, there will be better chances of getting the file faster at high download speed. 
### Trackers 
Trackers in a semi-decentralized network a tracker is a server which only function is to send the ip
addresses of all the peers in the swarm. In a decentralized network, all the peers are also trackers. 
### Torrent File
A torrent file is a file that contains meta-info (not the actual data) of the file that is being shared 
on the swarm by all peers connected to it. It normally has extension .torrent and contain useful info about
the trackers, and the pieces of the file being shared in the network such as length, SHA1 hashes of all the 
pieces.... see more details in Meta-info section below

### Torrent File Meta-info 

A torrent file contains all the meta-info related to the file you are willing to share in the network. 
 
* A torrent file contains a list of files and integrity metadata about all the pieces, and optionally contains a list of trackers.

* A torrent file is a Bencoded dictionary with the following keys (the keys in any Bencoded dictionary are lexicographically ordered):

  * announce: the URL of the tracker
  
  * info: this maps to a dictionary whose keys are dependent on whether one or more files are being shared:
      
    * files: a list of dictionaries each corresponding to a file (only when multiple files are being shared). Each dictionary has the following keys:

        * length: size of the file in bytes.
       
        * path: a list of strings corresponding to subdirectory names, the last of which is the actual file name
       
    * length: size of the file in bytes (only when one file is being shared)

    * name: suggested filename where the file is to be saved (if one file)/suggested directory name where the files are 
    to be saved (if multiple files)
    
    * piece length: number of bytes per piece. This is commonly 28 KiB = 256 KiB = 262,144 B.
    
    * pieces: a hash list, i.e., a concatenation of each piece's SHA-1 hash. As SHA-1 returns a 160-bit hash, pieces will 
    be a string whose length is a multiple of 20 bytes. If the torrent contains multiple files, the pieces are formed
     by concatenating the files in the order they appear in the files dictionary (i.e. all pieces in the torrent are the full piece length except for the last piece, which may be shorter).

All strings must be UTF-8 encoded, except for pieces, which contains binary data

## Client and Server Sockets Roles in P2P Networks

So far, our knowledge about how client and server sockets share data was based on client-server architecture. 
However, in a P2P network, we need to think about it differently because a peer is a server, client and tracker 
at the same time. In order to understand this concept better, let's organize our thoughts into the following two 
networking concepts; uploading and downloading. 

### Uploading Data to Other Peers
The upload process in a P2P network is easy to understand since is similar to the client-server architecture. 
Let's say that three peers P1, P2, and P3 are sharing a file in a swarm, and P1 is a seeder. Thus, P1 is uploading 
data to the network so P2, and P3 can download get that data. 

If you think about this situation, the clients sockets of P2 and P3 at some point connected to the server 
socket of P1, so P2 and P3 are requesting data to P1, and P1 (the server socket of P1) is sending that data 
to P2 and P3. This process is possible because a server socket can accept multiple clients (in this case the
client sockets of peers P2 and P3.). So, we can safely say that in order for a peer to upload data to other 
peers, it needs to have the server socket running and the clients of those peers need to be connected to that
server socket. Thus, we have here something similar to the way data is share in a centralized client-server architecture. 

### Downloading Data From Other Peers. 

Downloading data from other peers is a bit more complicated than uploading data. Think about the following use case.

Let's say, like in the uploading example, that three peers P1, P2, and P3 are sharing a file in a swarm, and P1 is a seeder.
In this case, let's assume that we are P2, and we are trying to download different pieces of the same file from P1 and P3 
at the same time. We already know that P2 must be running a client socket in order to download data from P1, but at 
the same time, the same client socket needs to download data from P3. However, that is not possible because 
P2 client socket is already blocking the port that it is using to connect with P1. We know from other labs that
a client socket can only connect to one server at the same time. 

So, how can we fix this problem? That is your job to figure it out in this lab. Please, use the space below to provide your 
best guess to solve this problem. You won't be penalized if you do not know the answers, but you'll be if 
you don't even try to provide an answer.

## Lab Implementation

One of the first things a peer/seeder must do is to decode a torrent file in order to extract useful info from it that 
will be used later to download/upload pieces of the file from/to other peers. 

Note that in this lab, we are assuming that we already have a torrent file (.torrent) although this is not always the 
case in real BitTorrent clients. Some of them have the capability to create their own torrent files from the original ones

Your job in this lab:

1. Download the age.torrent file from iLearn and put it in this lab folder. 

2. Implement all the methods marked as 'TODO' in torrent.py file. 

3. Test the lab by printing all the values extracted from the torrent file using the results of the methods 
you implemented in this lab. 

## References 

http://www.bittorrent.org/beps//bep_0005.html






 





