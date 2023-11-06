import socket
import struct


######### Connections ##########

# BUFFER_SIZE = 32  # Buffer Size for receiving file in chunks
serverName = "127.0.0.1"  # Server IP
serverPort = 12345  # Server Port Number
server_addr = (
    serverName,
    serverPort,
)  # Tuple to identify the UDP connection while sending

# FIXME
ip_source = "127.0.0.1"
ip_dest = "127.0.0.1"

######### Choose the file to download #########

print("test1.txt")
print("test2.txt")
print("Enter the file name to download:")

message = input()
user_data = message.encode()


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
# ip_total_length = len(user_data) + 28  # 20 bytes for IP header and 8 for udp header


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


# 可以先不干
# def checksum(msg):
#     s = 0
#     for i in range(0, len(msg), 2):
#         w = msg[i] + (msg[i + 1] << 8)
#         s = s + w
#     s = (s >> 16) + (s & 0xFFFF)
#     s = ~s & 0xFFFF
#     return s
# # TODO: update checksum
# udp_checksum = checksum(udp_header)
# udp_header = struct.pack(pseudo_header + udp_header + udp_checksum)


# final package
packet = ip_header + udp_header + user_data


################## UDP raw socket ###################
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
clientSocket.sendto(packet, (serverName, serverPort))
# 或者
# clientSocket.sendto(packet, (ip_dest, 0))
received_data, serverAddress = clientSocket.recvfrom(2048)
loop_back_header_offset = 20
ip_header_offset = 20
udp_header_offset = 8
data = received_data[loop_back_header_offset + ip_header_offset + udp_header_offset :]

# write the received file to disk
with open("received_file.txt", "wb") as file:
    byte, server = clientSocket.recvfrom(2048)
    file.write(byte[20:])
    print("Received file saved as 'received_file'")

print("Received packet from:", serverAddress)
clientSocket.close()
