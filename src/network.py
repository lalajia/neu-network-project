import socket
import struct
import random


def create_ip_packet(ip_source, ip_dest, udp_segment):
    ################## IP header ###################
    ip_version = 4  # ipv4
    ip_ihl = 5  # Header Length 5*32/8 = 20 bytes, no option
    # bit shift by 4 bits to the left, then add the ihl
    ip_ver_ihl = (ip_version << 4) + ip_ihl  # calculated by version and ihl

    ip_type_of_service = 0  # dscp
    ip_identification = random.randint(0, 65535)
    ip_fragment_offset = 0
    ip_time_to_live = 255
    ip_protocol = socket.IPPROTO_UDP  # UDP
    ip_saddr = socket.inet_aton(ip_source)
    ip_daddr = socket.inet_aton(ip_dest)
    # update length
    ip_total_length = len(udp_segment) + 20

    def ipv4_checksum(header):
        checksum = 0
        for i in range(0, len(header), 2):
            if i == 10:  # Skip the checksum field itself
                continue
            # Combine two bytes and add them to the checksum
            word = (header[i] << 8) + header[i + 1]
            checksum += word
            checksum = (checksum & 0xffff) + (checksum >> 16)
        # One's complement of the checksum
        checksum = ~checksum & 0xffff
        return checksum

    # B = 1 byte
    # H = 2 bytes
    # 4s = 4 bytes
    ip_header_without_checksum = struct.pack(
        "!BBHHHBBH4s4s",
        ip_ver_ihl,  # B
        ip_type_of_service,  # B
        ip_total_length,  # H
        ip_identification,  # H
        ip_fragment_offset,  # H
        ip_time_to_live,
        ip_protocol,
        0,
        ip_saddr,
        ip_daddr,
    )
    ip_header = struct.pack(
        "!BBHHHBBH4s4s",
        ip_ver_ihl,  # B
        ip_type_of_service,  # B
        ip_total_length,  # H
        ip_identification,  # H
        ip_fragment_offset,  # H
        ip_time_to_live,
        ip_protocol,
        ipv4_checksum(ip_header_without_checksum),
        ip_saddr,
        ip_daddr,
    )
    return ip_header + udp_segment


def unpack_ip_packet(ip_packet):
    ip_header = ip_packet[:20]
    ip_header = struct.unpack("!BBHHHBBH4s4s", ip_header)
    ip_version = ip_header[0] >> 4
    ip_header_length = (ip_header[0] & 0xF) * 4
    ip_ttl = ip_header[5]
    ip_protocol = ip_header[6]
    ip_source_address = socket.inet_ntoa(ip_header[8])
    ip_destination_address = socket.inet_ntoa(ip_header[9])
    udp_segment = ip_packet[ip_header_length:]
    return ip_version, ip_header_length, ip_ttl, ip_protocol, ip_source_address, ip_destination_address, udp_segment
