# neu-network-project

CS5700 Foundation of Network

# 1 How to run

cd src
In terminal: sudo python3 rawUDPServer.py
cd src
In a new terminal: sudo python3 rawUDPClient.py
input the file name to be downloaded

The results of the trasmission would be displayed in the resource folder.


# 2 The details for each python file in src folder
## 1 network.py
This component is to implement the netwrk layer including the creation of the ip datagram when sending packet, and how to unpack the packet received.

## 2 rawUDPClient.py
This component is to implent the logic of the client side. This involves the creation of the application layer protocol HTTP, the behavior of the client when receiving the file from the server and a main function for socket creation, request sending.