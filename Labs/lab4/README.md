# Lab #4: Threading clients in server side 

Note: for this lab, you need to include your client.py and server.py files implemented in labs 2 and 3. 

In lab #3, hopefully you created a server program that handles client connections, process requests, and 
send responses back to clients using client handlers. However, this server can only handle one connection
at a time. In other words, only one client can connect to this server. Real world servers are 
prepared to handle multiple connections from multiple clients at the same time. In this lab, you will learn how to 
handle multiple connections in your server. 

First of all, lets see what we have so far: 

```python
# basic example of accepting a client in server side.
# this example assumes the server is already listening
# assume this function exists:

def handler(self, clienthandler):
    # do something with the clienthandler.
    pass

def accept_clients():
    while True:
        clienthandler, addr = serversocket.accept() 
        handler(clienthandler) # do something with the clienthandler. 
```
The above code is blocking the main thread in the server side when a client is accepted because the 
handler will be calling the clienthandler.recv() method waiting for client messages. Therefore, only one 
client can use the server at a time. If another client wants to use the server, it needs to wait until the
first client disconnects from the server. Obviously, our server must support multiple and simultaneous
client connections to meet the basic requirements enforced by modern apps.  

### How can we fix it? 

In order to fix this, we need to thread clients. There are many ways to create threads in Python. The following code 
shows one of the easiest way of implementing that functionality. 

```python
# basic example of accepting a client in server side.
# this example assumes the server is already listening. 
from threading import Thread 
from client_handler import ClientHandler

def handler(self, clienthandler):
    # do something with the clienthandler (i.e send data to the client)
    pass

def accept_clients():
    while True:
        clientsocket, addr = serversocket.accept()
        Thread(target=thread_client, args=(clientsocket, addr)).start() # client thread started   
```

The above code creates a thread of the handler method that is handling a specific client. That way, clients
won't block the main thread, and other clients can request data at the same time. But, is this the ideal 
situation in a server? Not at all. We can rely in simple method functionality for basic servers. However. 
for bigger servers, the handler should be a class implementing many methods. 

## The ClientHandler Class 

The client handler class provides a clean way to deal with multiple clients in our client-server architecture.
It provides great advantages such as encapsulating data processing separately from the server class. Therefore, 
we can rehuse our server class in other applications. The following is an example of a ClientHandler class

```python
import pickle
class ClientHandler(object):
 
    def __init__(self, server_instance, clientsocket, addr):
          # the server instance is passed as self by the server. 
          # so the class has access to all the server methods in running time
          # code omitted
          self.server_ip = addr[0]
          self.client_id = addr[1]
          self.server = server_instance
          self.handler = clientsocket
          pass
   
    def do_something(self):
          # code omitted
          pass
    def send(self, data): 
         serialized_data = pickle.dumps(data)
         self.handler.send(data)
         
    def receive(self, max_mem_alloc=4096):
         raw_data = self.handler.recv(max_mem_alloc)
         data = pickle.loads(raw_data)
         return data
    
    def run(self):
         self.do_something()
         
```

### How do we thread the a object of the ClientHandler class?

Easy, just modifying the handler method and giving it a more appropiate name such as thread_client. Then, we
create an object of the ClientHandler class inside the method, passing all the appropiate parameters 

```python
# basic example of accepting a client in server side.
# this example assumes the server is already listening

import ClientHandler 
from threading import Thread

def threaded_client(clientsocket, addr):
    client_id = addr[1]
    client_handler = ClientHandler(self, clientsocket, addr) # self is the server instance
    client_handler.run() # inits all the components in client handler object
    #  adds the client handler object to the list of all the clients objects created by this server. 
    #  key: client id, value: client handler
    client_handlers[client_id] = client_handler # assumes dict was initialized in class constructor
   
def accept_clients():
    while True:
        clienthandler, addr = serversocket.accept() 
        # creeate new client thread. 
        Thread(target=threaded_client, args=(clienthandler, addr)).start() 
```

### Dealing with race conditions. 

Is the threading clients process enough to keep our server under optimal performance? 

In real world servers, supporting multiple clients at a time, race conditions must be handled because two clients
may try to write into the memory allocation at the same time. Therefore, we also need to implement a lock mechanisms in 
the server side to avoid race conditions. The following code example will help you to avoid race conditions in 
your server

```python
import threading
write_lock = threading.Lock() # creates the lock

# lock adquired only client1 can write in memory allocation
write_lock.acquire() 
# clienthandler1 writes in the memory allocation
write_lock.release() # lock is released
# other clients now can adquire the lock to write in the same memory allocation. 
```

## Lab Guidelines 

In this lab, you are given an empty template of the ClientHandler class, and you will be using your client
and server classes from previous labs.

### Client class
Add a copy of your client class from lab #3 to this lab folder.

### ClientHandler class: 
1. The client handler class should have a method to process the data from your client in lab #2. This data is
your name, student id, and github username.
2. Create a print_lock so only one clienthandler can log/print the data on the server console at a time

### Server class: 
1. Add a copy of your server class from lab #3 to this lab folder.
2. Modify new server class, so it can thread clients to support multiple client connections. follow examples given 
in this README file
2. The server should show the same output as the instructor's server when testing your client in lab #2. 
It should show in your server windows your name, student id and github username, 

## Testing your program

1. The server: open a terminal windows in your machine, and run your server at 127.0.0.1/12000. 
2. Client 1: open a different terminal windows in the same machine and run your client to connect to the
above server 
3. Client 2: open a different terminal windows than server and client 1 in the same machine and run your client to connect to the
above server 

For each client that connects to your server, the server should output in console the name, student id, and 
github username from the user connecting to the server. You are free to hard code this data in your
ClientHandler before running each client, or you can ask this info by user input in the client side. 

### Now that you have completed labs 0 to 4, you have the proper networking knowledge to complete the TCP Centralized 
Multi-threading Client-Server Network Project








