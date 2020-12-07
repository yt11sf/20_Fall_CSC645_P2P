# LAB 6 P2P BitTorrent Protocol: A Trackerless Decentralized Network 

In last lab, students learned in detail about P2P networks and how they work. However, in order to work properly, 
P2P networks need to be handled by communication protocols that define what and how data is shared in the network. 
The BitTorrent protocol is commonly used in many implementations of P2P networks because it provides good general performance. 

## How Does BitTorrent Work?

BitTorrent is a peer-to-peer protocol which means that data in a swarm is shared without the need of a central server 
(in theory). Traditionally, in a P2P network using the bitTorrent protocol, a peer joins the network by connecting a
tracker which has all the IP addresses of the peers connected to that network. Then, that peer will send connections 
requests to all those peers in the network. Once, that peer is connected to the network, it can download or upload pieces
of the file that is being shared in that network

Users downloading from a bitTorrent swarm are usually referred as Lechers and Peers. Users that remain connected to a 
bitTorrent swarm after the file has been completely downloaded (seeder) contribute to the good performance of the network because 
they contribute to the increase of the downloading rates in the swarm. If a swarm has no seeders, then other users 
won´t be able to download the complete file from the swarm. That is why seeders are really important in P2P networks 
using the bitTorrent protocol. 

BitTorrent clients reward other clients who upload, preferring to send data to clients who contribute more upload 
bandwidth rather than sending data to clients who upload at a very slow speed. This speeds up download times 
for the swarm as a whole and rewards users who contribute more upload bandwidth.

## Trackers and Trackerless Networks 

In our definition of how a P2P network using bitTorrent protocol works, we said that it is a decentralized network "in 
theory". Usually, that is not entirely true because there are many P2P networks that need a central server to perform 
some specific services in the network (i.e the tracker). One of the challenges in a decentralized BitTorrent network 
is to make it tracker-less. Decentralized bitTorrent networks use DHT technology to accomplish that goal. 

## Distributed Hash Table (DHT) 

Please note the terminology used in this document to avoid confusion. A "peer" is a client/server listening on a TCP 
port that implements the BitTorrent protocol. A "node" is a client/server listening on a UDP port implementing 
the distributed hash table protocol. Take into consideration that in this lab we use the same TCP connection for 
server and tracker. So, no need to implement a new server and client using UDP sockets. 

BitTorrent uses a "distributed hash table" (DHT) for "trackerless" torrents. At that effect, each peer becomes a tracker, 
and it removes the need of a central tracker. Nodes (peers) supporting DHT must implement a routing table where every 
node maintains a table of good nodes (responded to queries within the last 15 minutes) as starting points for queries 
in the DHT. BitTorrent extended the protocol to support UDP connections as well with DHT. 

## DHT Routing Table 

The routing table in a DHT implementation supports values such as unique NodeID (SHA1 hash of ip address concatenated 
onto a secret key), distance from one node to another one, IP address and port of such node. The routing table only 
maintains a small amount of nodes in buckets (sequentially allocated). When a good node is received, it replaces a bad
node. If there are no bad nodes, then the 'last changed' property is inspected, and older buckets are replaced by 
the new ones.  

## Torrent File DHT Extension

A trackerless torrent does not have announces. Instead, it has a a list of "nodes keys": 

```
nodes = [["<host>", <port>], ["<host>", <port>], ...]
nodes = [["127.0.0.1", 6881], ["your.router.node", 4804], ["2001:db8:100:0:d5c8:db3f:995e:c0f7", 1941]]
```

One of the main problems faced by trackerless implementations is that every peer/node needs to connect to an initial node
in order to retrieve an initial DHT. Once, the initial DHT is retrieved, the peer can create its own routing table of
good nodes, independently of the routing table from other nodes. Thus, every torrent file must have at least one "node
key" defined in its meta-info. 

## KRPC Protocol

The KRPC (remote procedure calls protocol) is a simple message mechanism that maintains a reliable communication between
two or mode nodes used by DHT to interchange queries between nodes

The KRPC protocol implements a dictionary with the following key/values:

```
General:

't' = Transaction id of the query encode in 2 characters string values. For instance, 't':'aa'
'y' = type of transaction. Values: 'q' query, 'r' response, 'e' error

Query Messages:

'q' = The method name of the query. For instance, 'q':'get_peers'
'a' = A dictionary value containing the named arguments of the query

Response Messages (only sent upon succesful conplexion of a query): 
'r' = dictionary containing named return values

Errors: 
201 Generic Error
202 Server Error
203 Protocol Error, such as a malformed packet, invalid arguments, or bad token
204 Method Unknown

generic error example = {"t":"aa", "y":"e", "e":[201, "A Generic Error Ocurred"]}
```

## DHT Query 

All queries must have a unique id in the query and response. 

### ping 

The most basic query is a ping. "q" = "ping" A ping query has a single argument, "id" the value is a 20-byte string containing the senders node ID in network byte order. The appropriate response to a ping has a single key "id" containing the node ID of the responding node.

arguments:  {"id" : "querying nodes id"}

response: {"id" : "queried nodes id"}

Example: 


```
ping Query = {"t":"aa", "y":"q", "q":"ping", "a":{"id":"abcdefghij0123456789"}}
bencoded = d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe
Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
```

### find_node

Find node is used to find the contact information for a node given its ID. "q" == "find_node" A find_node query has two arguments, "id" containing the node ID of the querying node, and "target" containing the ID of the node sought by the queryer. When a node receives a find_node query, it should respond with a key "nodes" and value of a string containing the compact node info for the target node or the K (8) closest good nodes in its own routing table.

arguments:  {"id" : "<querying nodes id>", "target" : "<id of target node>"}

response: {"id" : "<queried nodes id>", "nodes" : "<compact node info>"}

Example Packets

```
find_node Query = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":"abcdefghij0123456789", "target":"mnopqrstuvwxyz123456"}}
bencoded = d1:ad2:id20:abcdefghij01234567896:target20:mnopqrstuvwxyz123456e1:q9:find_node1:t2:aa1:y1:qe
Response = {"t":"aa", "y":"r", "r": {"id":"0123456789abcdefghij", "nodes": "def456..."}}
bencoded = d1:rd2:id20:0123456789abcdefghij5:nodes9:def456...e1:t2:aa1:y1:re
```

### get_peers

Get peers associated with a torrent infohash. "q" = "get_peers" A get_peers query has two arguments, "id" containing the node ID of the querying node, and "info_hash" containing the infohash of the torrent. If the queried node has peers for the infohash, they are returned in a key "values" as a list of strings. Each string containing "compact" format peer information for a single peer. If the queried node has no peers for the infohash, a key "nodes" is returned containing the K nodes in the queried nodes routing table closest to the infohash supplied in the query. In either case a "token" key is also included in the return value. The token value is a required argument for a future announce_peer query. The token value should be a short binary string.

arguments:  {"id" : "<querying nodes id>", "info_hash" : "<20-byte infohash of target torrent>"}

response: {"id" : "<queried nodes id>", "token" :"<opaque write token>", "values" : ["<peer 1 info string>", "<peer 2 info string>"]}

or: {"id" : "<queried nodes id>", "token" :"<opaque write token>", "nodes" : "<compact node info>"}

Example Packets:

```
get_peers Query = {"t":"aa", "y":"q", "q":"get_peers", "a": {"id":"abcdefghij0123456789", "info_hash":"mnopqrstuvwxyz123456"}}
bencoded = d1:ad2:id20:abcdefghij01234567899:info_hash20:mnopqrstuvwxyz123456e1:q9:get_peers1:t2:aa1:y1:qe

Response with peers = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "values": ["axje.u", "idhtnm"]}}
bencoded = d1:rd2:id20:abcdefghij01234567895:token8:aoeusnth6:valuesl6:axje.u6:idhtnmee1:t2:aa1:y1:re

Response with closest nodes = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "nodes": "def456..."}}
bencoded = d1:rd2:id20:abcdefghij01234567895:nodes9:def456...5:token8:aoeusnthe1:t2:aa1:y1:re
```

### announce_peer

Announce that the peer, controlling the querying node, is downloading a torrent on a port. announce_peer has four arguments: "id" containing the node ID of the querying node, "info_hash" containing the infohash of the torrent, "port" containing the port as an integer, and the "token" received in response to a previous get_peers query. The queried node must verify that the token was previously sent to the same IP address as the querying node. Then the queried node should store the IP address of the querying node and the supplied port number under the infohash in its store of peer contact information.

There is an optional argument called implied_port which value is either 0 or 1. If it is present and non-zero, the port argument should be ignored and the source port of the UDP packet should be used as the peer's port instead. This is useful for peers behind a NAT that may not know their external port, and supporting uTP, they accept incoming connections on the same port as the DHT port.

```
arguments:  {"id" : "<querying nodes id>",
  "implied_port": <0 or 1>,
  "info_hash" : "<20-byte infohash of target torrent>",
  "port" : <port number>,
  "token" : "<opaque token>"}

response: {"id" : "<queried nodes id>"}
```

Example Packets:

```
announce_peers Query = {"t":"aa", "y":"q", "q":"announce_peer", "a": {"id":"abcdefghij0123456789", "implied_port": 1, "info_hash":"mnopqrstuvwxyz123456", "port": 6881, "token": "aoeusnth"}}
bencoded = d1:ad2:id20:abcdefghij012345678912:implied_porti1e9:info_hash20:mnopqrstuvwxyz1234564:porti6881e5:token8:aoeusnthe1:q13:announce_peer1:t2:aa1:y1:qe

Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
```


# Lab Implementation

In this lab, your work is to create a basic tracker implementation supporting DHT based on all the reading from
this lab. A tracker (template) and peer file are provided for the complexion of this lab. Additionally, and in order to test 
this lab, you will need to use your client and server files from lab 4 or the ones from your project #1

Provide implementation only for methods marked with 'TODO' only in tracker.py. 

## Lab Testing

1. Make sure that your tracker is set to 'announce'. 

2. Open a terminal windows and run the peer.py file.

3. Open your peer.py file, change the server port, and set the tracker's announce parameter to 'None'

4. This is the sample output printed by the first tracker: 

```python

# ping query
ping Query = {"t":"aa", "y":"q", "q":"ping", "a":{"id":"abcdefghij0123456789"}}
bencoded = d1:ad2:id20:abcdefghij0123456789e1:q4:ping1:t2:aa1:y1:qe

# find_node query
find_node Query = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":"abcdefghij0123456789", "target":"mnopqrstuvwxyz123456"}}
bencoded = d1:ad2:id20:abcdefghij01234567896:target20:mnopqrstuvwxyz123456e1:q9:find_node1:t2:aa1:y1:qe

# get_peers query
get_peers Query = {"t":"aa", "y":"q", "q":"get_peers", "a": {"id":"abcdefghij0123456789", "info_hash":"mnopqrstuvwxyz123456"}}
bencoded = d1:ad2:id20:abcdefghij01234567899:info_hash20:mnopqrstuvwxyz123456e1:q9:get_peers1:t2:aa1:y1:qe

# announce_peers query
announce_peers Query = {"t":"aa", "y":"q", "q":"announce_peer", "a": {"id":"abcdefghij0123456789", "implied_port": 1, "info_hash":"mnopqrstuvwxyz123456", "port": 6881, "token": "aoeusnth"}}
bencoded = d1:ad2:id20:abcdefghij012345678912:implied_porti1e9:info_hash20:mnopqrstuvwxyz1234564:porti6881e5:token8:aoeusnthe1:q13:announce_peer1:t2:aa1:y1:qe
```

5. This is the sample output printed by the second tracker

```python
# ping response
Response = {"t":"aa", "y":"r", "r": {"id":"0123456789abcdefghij", "nodes": "def456..."}}
bencoded = d1:rd2:id20:0123456789abcdefghij5:nodes9:def456...e1:t2:aa1:y1:re

# find_node resppnse
Response = {"t":"aa", "y":"r", "r": {"id":"0123456789abcdefghij", "nodes": "def456..."}}
bencoded = d1:rd2:id20:0123456789abcdefghij5:nodes9:def456...e1:t2:aa1:y1:re

# get_peers response
Response with peers = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "values": ["axje.u", "idhtnm"]}}
bencoded = d1:rd2:id20:abcdefghij01234567895:token8:aoeusnth6:valuesl6:axje.u6:idhtnmee1:t2:aa1:y1:re

# announce_peer response
Response with closest nodes = {"t":"aa", "y":"r", "r": {"id":"abcdefghij0123456789", "token":"aoeusnth", "nodes": "def456..."}}
bencoded = d1:rd2:id20:abcdefghij01234567895:nodes9:def456...5:token8:aoeusnthe1:t2:aa1:y1:re

# announce_peers response
Response = {"t":"aa", "y":"r", "r": {"id":"mnopqrstuvwxyz123456"}}
bencoded = d1:rd2:id20:mnopqrstuvwxyz123456e1:t2:aa1:y1:re
```


Note that your values for steps 4 and 5 may be different. I am more interested in students understanding the process 
than in the output of the lab.



## References: 

http://www.bittorrent.org/beps//bep_0005.html


 






