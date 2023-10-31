import socket
import struct


s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)


# Replace with your own IP address
server_ip = "your_own_ip_address"
s.bind((server_ip, 0))


while True:
    packet, addr = s.recvfrom(2048)

    # The IP header is the first 20 bytes of the packet
    ip_header = packet[:20]

    # Unpack the IP header
    iph = struct.unpack("!BBHHHBBH4s4s", ip_header)

    # The data starts after the IP header and the UDP header (8 bytes)
    data = packet[28:]

    print("Received packet from:", addr)
    print("Data:", data.decode())
