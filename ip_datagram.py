import socket
import struct

def create_ip_datagram(ip_source, ip_dest, segment):
    ip_version = 4  # ipv4
    ip_ihl = 5  # Header Length =5, no option
    ip_type_of_service = 0  # dscp
    ip_total_length = len(segment) + 20  # TODO: to be updated
    ip_identification = 54321
    ip_flags = 0
    ip_fragment_offset = 0
    ip_time_to_live = 255
    ip_protocol = 253
    ip_header_checksum = 0  # TODO: to be updated
    ip_saddr = socket.inet_aton(ip_source)
    ip_daddr = socket.inet_aton(ip_dest)
    ip_ver_ihl = (ip_version << 4) + ip_ihl  # calculated by version and ihl


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

    return ip_header + segment