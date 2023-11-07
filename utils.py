import os
import socket
import struct
import udp_segment
import ip_datagram

def fragment_data(data, udp_payload_size=508):
    fragments = []
    for i in range(0, len(data), udp_payload_size):
        fragments.append(data[i: i + udp_payload_size])
    return fragments

def readFile(filename):
    # if file exists, read the file else print error message
    if os.path.exists(filename):
        with open(filename, "rb") as file:
            file_data = file.read()
            return file_data
    else:
        print("File does not exist")
        return None

def receive_packet(rawSocket):
    packet, addr = rawSocket.recvfrom(65535)
    # Parse the packet (20 bytes for IP header and 8 bytes for UDP header)
    ip_header = packet[20:40]
    udp_header = packet[40:48]
    payload = packet[48:]
    
    # Unpack the IP header and UDP header
    ip_header_data = struct.unpack("!BBHHHBBH4s4s", ip_header)
    udp_header_data = struct.unpack("!HHHH", udp_header)
    
    # Extract data from the headers
    source_ip = socket.inet_ntoa(ip_header_data[8])
    source_port = udp_header_data[0]
    message = payload.decode("utf-8")
    
    print(f"Received message from {source_ip}:{source_port}: {message}")
    return message, source_ip, source_port

# input the payload, create the UDP segment and IP datagram, and send the packet
def send_data(rawSocket, payload, source_ip, source_port, destination_ip, destination_port):
    #check if the payload is empty
    if not payload:
        return
    # fragment the data
    fragments = fragment_data(payload)
    # send the fragments
    for fragment in fragments:
        segment = udp_segment.create_udp_segment(source_port, destination_port, fragment)
        datagram = ip_datagram.create_ip_datagram(source_ip, destination_ip, segment)
        rawSocket.sendto(datagram, (destination_ip, destination_port))
    # segment = udp_segment.create_udp_segment(source_port, destination_port, payload)
    # datagram = ip_datagram.create_ip_datagram(source_ip, destination_ip, segment)
    # rawSocket.sendto(datagram, (destination_ip, destination_port))