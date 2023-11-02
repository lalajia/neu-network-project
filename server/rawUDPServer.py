import socket
import struct


s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
######### Connections ##########

# FIXME: # Bind to the desired network interface and port
# server_port = 12345
# server_addr = ('', server_port)
# s.bind(server_addr)
# print("Starting server on port:", server_port)

server_name = "127.0.0.1"  # Server IP
server_port = 12345  # Server Port Number
server_addr = (
    server_name,
    server_port,
)  # Tuple to identify the UDP connection while sending

s.bind(server_addr)
print("Starting server on port: ", server_port)


###################### Connecting ###################
while True:
    packet, client_addr = s.recvfrom(2048)

    # Calculate the offset for custom headers
    ip_header_offset = 20  # Adjust this based on your custom IP header
    udp_header_offset = 28  # Adjust this based on your custom UDP header
    data = packet[ip_header_offset + udp_header_offset :]

    print("Received packet from:", client_addr)
    print("File:", data.decode())
