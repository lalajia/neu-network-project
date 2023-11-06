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

user_data = ("message").encode()
ip_source = "127.0.0.1"
ip_dest = "127.0.0.1"

################## UDP header ###################

# TODO: need pseudo header

# upd header
udp_source_port = 12345
udp_destination_port = 54321
udp_length = len(user_data) + 8
udp_checksum = 0


udp_header = struct.pack(
    "!HHHH", udp_source_port, udp_destination_port, udp_length, udp_checksum
)

################## IP header ###################
ip_version = 4  # ipv4
ip_ihl = 5  # Header Length =5, no option
ip_type_of_service = 0  # dscp
ip_total_length = 20  # TODO: to be updated
ip_identification = 54321
ip_flags = 0
ip_fragment_offset = 0
ip_time_to_live = 255
ip_protocol = 17
ip_header_checksum = 0  # TODO: to be updated
ip_saddr = socket.inet_aton(ip_source)
ip_daddr = socket.inet_aton(ip_dest)
ip_ver_ihl = (ip_version << 4) + ip_ihl  # calculated by version and ihl

# # update length
# ip_total_length = len(user_data) + 28  # 20 bytes for IP header


ip_header = struct.pack(
    "!BBHHHBBH4s4s",
    ip_ver_ihl,
    ip_type_of_service,
    ip_total_length,
    ip_identification,
    ip_fragment_offset,
    ip_time_to_live,
    ip_protocol,
    ip_header_checksum,
    ip_saddr,
    ip_daddr,
)


# final package
packet = ip_header + udp_header + user_data


###################### Connecting ###################
while True:
    packet, client_addr = s.recvfrom(2048)

    loop_back_header_offset = 20

    # Calculate the offset for custom headers
    ip_header_offset = 20
    udp_header_offset = 8
    data = packet[loop_back_header_offset + ip_header_offset + udp_header_offset :]
    print("data is ", data)
    # file_name = data.decode()
    with open(data, "rb") as file:
        file_data = file.read()
        print(file_data)

    s.sendto(file_data, client_addr)
    #
    # Send the content of the file back to the client

    print("Received data", packet)
    print("Received packet from:", client_addr)
    print("File:", data.decode())
