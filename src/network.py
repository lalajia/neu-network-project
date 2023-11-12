import socket
import struct
import random
from sys import platform


def pack_helper(ip_ver_ihl, ip_type_of_service, ip_total_length, ip_identification, ip_fragment_offset, ip_time_to_live,
                ip_protocol, checksum, ip_saddr, ip_daddr):
    # if the system is macOS, pack fragmentation offset as little indian
    if platform == "darwin":
        be_header_part1 = struct.pack(
            "!BB",  # Big-endian format
            ip_ver_ihl,  # B
            ip_type_of_service,  # B
        )
        packed_ip_total_length = struct.pack("<H", ip_total_length)
        packed_ip_identification = struct.pack("!H", ip_identification)
        packed_ip_fragment_offset = struct.pack("<H", ip_fragment_offset)
        be_header_part2 = struct.pack(
            "!BBH4s4s",  # Big-endian format
            ip_time_to_live,  # B
            ip_protocol,  # B
            checksum,
            ip_saddr,
            ip_daddr
        )
        return be_header_part1 + packed_ip_total_length + packed_ip_identification + packed_ip_fragment_offset + \
            be_header_part2
    else:
        return struct.pack(
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
    ip_header_without_checksum = pack_helper(ip_ver_ihl, ip_type_of_service, ip_total_length, ip_identification,
                                             ip_fragment_offset, ip_time_to_live, ip_protocol, 0, ip_saddr,
                                             ip_daddr)
    ip_header = pack_helper(
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



def unpack_helper(ip_header):
    if platform == "darwin":
        part1 = struct.unpack("!BB", ip_header[:2])
        # Unpack little-endian fields
        part2 = struct.unpack("<H", ip_header[2:4])
        # Unpack big-endian fields
        part3 = struct.unpack("!H", ip_header[4:6])
        # Unpack little-endian fields
        part4 = struct.unpack("<H", ip_header[6:8])
        # Unpack the rest of the big-endian fields
        part5 = struct.unpack("!BBH", ip_header[8:])
        ip_header = part1 + part2 + part3 + part4 + part5
    else:
        ip_header = struct.unpack("!BBHHHBBH4s4s", ip_header)
    return ip_header

def unpack_ip_packet(ip_packet):
    ip_header = ip_packet[:20]
    ip_header = unpack_helper(ip_header)
    ip_version = ip_header[0] >> 4
    ip_header_length = (ip_header[0] & 0xF) * 4
    ip_ttl = ip_header[5]
    ip_protocol = ip_header[6]
    ip_source_address = socket.inet_ntoa(ip_header[8])
    ip_destination_address = socket.inet_ntoa(ip_header[9])
    udp_segment = ip_packet[ip_header_length:]
    # chop off the 20 bytes loopback header on macOS if the packet is from the same machine
    if platform == "darwin" and ip_source_address == ip_destination_address:
        udp_segment = udp_segment[20:]
    return ip_version, ip_header_length, ip_ttl, ip_protocol, ip_source_address, ip_destination_address, udp_segment
