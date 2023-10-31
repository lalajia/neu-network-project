from socket import *
import struct


######### Connections ##########
# 抄的

# BUFFER_SIZE = 32  # Buffer Size for receiving file in chunks
serverName = gethostname()  # Server IP
serverPort = 12345  # Server Port Number
server_addr = (
    serverName,
    serverPort,
)  # Tuple to identify the UDP connection while sending
ip_source = "127.0.0.1"
ip_dest = ""

######### Choose the file to download #########

print("Enter the file name to download:")
print("test1")
print("test2")
message = input()
user_data = message.encode()


################## IP header ###################
ip_version = 4  # ipv4
ip_ihl = 5  # Header Length =5, no option
ip_type_of_service = 0  # dscp
ip_total_length = 0  # TODO: to be updated
ip_identification = 54321
ip_flags = 0
ip_fragment_offset = 0
ip_time_to_live = 255
ip_protocol = socket.IPPROTO_UDP
ip_header_checksum = 0  # TODO: to be updated
ip_saddr = socket.inet_aton(socket.AF_INET, ip_source)
ip_daddr = socket.inet_aton(socket.AF_INET, ip_dest)
ip_ver_ihl = (ip_version << 4) + ip_ihl  # calculated by version and ihl

# update length
ip_total_length = len(user_data) + 20


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
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()
