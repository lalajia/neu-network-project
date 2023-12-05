# neu-network-project

# 1. How to run

- Use our Infrasturcture
  After obtaining password from the admin of the site, you can login to the server at:
  `ssh -p 5700 user@ztybigcat.me`
  and log into the client server at:
  `ssh -p 5701 user@ztybigcat.me`

Then you can run the program, type your file name and it will start to transfer.
_Note about our infrastucture_: we run our virtual machine on PROxMOX hypervisor platform. The virtual machines are bridged to LAN so they can contact each other.

- Run on your own machine
  Our application only support Linux and macOS opperation systems. For macOS, IPPROTO_RAW is used. For Linux, IPPROTO_UDP is used.
  If the user want to run this application, change the server_ip to any ip address of a server that the client can be reached, the client_ip to the real client ip address. For example the local ip address 127.0.0.1 can be used as both client and server if you want to test them on the loopback interface. The corresponding code are the line 114 and 115 in rawUDPClient.py and line 98 in rawUDPServer.py.

- The basic steps to run the application
  cd src
  In terminal: sudo python3 rawUDPServer.py
  cd src
  In a new terminal: sudo python3 rawUDPClient.py
  input the file name to be downloaded

# 2. How your application works

## Project Structure:

- resources
  - client
  - server
- src
  - network.py
  - rawUDPClient.py
  - rawUDPServer.py
  - transport.py
  - util.py

## The design and key functionalities of your application programs

### resources

The files downloaded by the client are stored in the client folder.
The files under the server folder are ready to be downloaded by the client.

### network.py

This file provides functionality to create and unpack IP packets. It includes functions to pack an IP packet with a UDP segment, as well as unpacking information from a received IP packet. The IP checksum calculation function is included in this file as well.

### rawUDPClient.py

This component is to implent the logic of the client side. This involves the creation of the application layer protocol HTTP, the behavior of the client when receiving the file from the server and a main function for socket creation, request sending and acknowledgement handling. The receive_file function manages the complexities of receiving and ordering file fragments, including handling out-of-order packets and checksum verification.

### rawUDPServer.py

This file is a server implementation for a UDP&IP file transfer protocol. It listens for incoming UDP packets with an IP and port, extracts requests for files from the packets, and responds by sending the requested file or an error response back to the client. It includes functions for extracting acknowledgment numbers, checking file existence, preparing HTTP responses, sending UDP packets, handling acknowledgment receptions, handling file-not-found scenarios, and initiating file transmissions. When sending file, a timeout retransmission function and a slidewindow function are utilized to optimise the transmission process (in our case, the timeout value is 25ms and the size of the slidewindow is 100(100 packets)).

### transport.py

This file provides functions for packing and unpacking with UDP segments as well as the udp checksum function. It creates UDP segments with specified source and destination ports, payload, and checksum. Additionally, it provides functions to unpack and extract information from a given UDP segment, including source and destination ports, length, checksum, and payload. The functions are used in rawUDPClient.py and rawUDPServer.py

### util.py

This file defines functions for managing resource folder. It provides methods to obtain the resource directory for the server and client components, allowing easy access to project resources. Additionally, it offers a function to split a given data sequence into fragments of a specified size for UDP communication applications(in our case, the size of the fragment is 1400 bytes).

# 3. Errors or use cases that have limitations

- Windows is not supported or tested.
- We do not implement multithreading to send ACK in a seprate thread, rather we implemented sliding window and selective repeat to speed up the transfer, however, the performance

# 4. If it doesn't meet any of the requirements

We've implemented all the requirments, including checksum, sequence Numbers, Acknowledgement numbers and Retransmission due to timeout.

# 5. Features that you have implemented

Details description of each function could be seen before each function.

## Features

### Headers Construction(Xinyue Zheng)

#### IP Headers

- **Construction Function:** `create_ip_packet(ip_source, ip_dest, udp_segment)`
  - This function constructs an IPv4 packet by creating the IP header and appending the provided UDP segment.
  - IP header fields include version, header length, type of service, total length, identification, fragment offset, time to live, protocol, header checksum, source IP address, and destination IP address.

#### UDP Headers

- **Construction Function:** `create_udp_segment(payload, source_ip, source_port, dest_ip, dest_port)`
  - The UDP header is constructed within this function along with a provided payload.
  - UDP header fields include source port, destination port, total length, and checksum.

### Checksum (Xinyue Zheng & Yonglan Qi)

#### IP Checksum

- **Function for Checksum Calculation:** `ipv4_checksum(header)`
  - Calculates the checksum for the IP header.
  - Utilizes one's complement arithmetic for checksum calculation.

#### UDP Checksum

- **Function for Checksum Calculation:** `udp_checksum_calc(udp_segment, source_ip, dest_ip)`
  - Calculates the checksum for the UDP segment.
  - Handles padding if the segment has an odd number of bytes.

### Sequence Numbers and Acknowledgement Numbers (Yonglan Qi)

- **Sequence Number Handling:**

  - Sequence numbers are used to keep track of the order of packets being sent.
  - Sequence numbers are included in the HTTP response headers in the server code (`prepare_http_response`).
  - The client extracts the sequence number from the received acknowledgment to determine the order of packets.

- **Acknowledgment Number Handling:**
  - The client sends acknowledgment messages to the server, indicating the successful reception of a packet.
  - The server extracts the acknowledgment number from these messages (`extract_ack_number`).

### Retransmission due to Timeout (Tianyi Zhang)

- **Timeout Mechanism:**
  - The server employs a timeout mechanism to retransmit packets if acknowledgments are not received within a specified timeout interval.
  - Timeout duration is defined as `TIMEOUT` in the server code.

### Sliding Window (Tianyi Zhang)

- **Sliding Window ans Selective Repeat:**
  - Sliding window is implemented in the server code (`send_file` function) using the variables `window_base` and `window_end`.
  - The window dynamically adjusts based on acknowledgments received.
  - Selective repeat is achieved by checking whether the sequence number (`seq_num`) is present in the set of `acked_sequence_numbers`. If a packet with sequence number `seq_num` is acknowledged, it means the receiver has successfully received the packet, and `seq_num` is removed from the set.
  - If a packet within the window has not been acknowledged and a timeout occurs, the packet is retransmitted.

# 6. Lessons learned

-

# 7. Possible future improvements

- Adapt multithreading function to optimise the transmission efficiency.
- Combine other group's great ideas with ours to improve the file transmission performance.
- Test and debug our application for Windows operation system.
