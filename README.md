# neu-network-project

CS5700 Foundation of Network

- cd src
- In terminal: sudo python3 rawUDPServer.py
- cd src
- In a new terminal: sudo python3 rawUDPClient.py
- input the file name to be downloaded

The results of the trasmission would be displayed in the resource folder.

# 2 The details for each python file in src folder

## 1 network.py

This component is to implement the netwrk layer including the creation of the ip datagram when sending packet, and how to unpack the packet received.

## 2 rawUDPClient.py

This component is to implent the logic of the client side. This involves the creation of the application layer protocol HTTP, the behavior of the client when receiving the file from the server and a main function for socket creation, request sending.

## 3 rawUDPServer.py

This file is a server implementation for a UDP&IP file transfer protocol. It listens for incoming UDP packets with an IP and port, extracts requests for files from the packets, and responds by sending the requested file or an error response back to the client. It handles packet fragmentation, waits for acknowledgment (ACK) packets from the client, and retransmits packets if no ACK is received within a timeout period.

## 4 transport.py

This file provides functions for packing and unpacking with UDP segments. It creates UDP segments with specified source and destination ports, payload, and checksum. Additionally, it provides functions to unpack and extract information from a given UDP segment, including source and destination ports, length, checksum, and payload. The functions are used in rawUDPClient.py and rawUDPServer.py

## 5 util.py

This file defines functions for managing resource folder. It provides methods to obtain the resource directory for the server and client components, allowing easy access to project resources. Additionally, it offers a function to split a given data sequence into fragments of a specified size for UDP communication applications.

## 6 reference

[Cannot build raw on MAC/Windows](https://stackoverflow.com/questions/49530269/python-socket-setsockopt-with-raw-socket)
