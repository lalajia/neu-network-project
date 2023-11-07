# this function is used for create a udp segment
import socket
import struct

def create_udp_segment(udp_source_port, udp_destination_port, message):
    udp_length = len(message) + 8
    udp_checksum = 0


    udp_header = struct.pack(
        "!HHHH", udp_source_port, udp_destination_port, udp_length, udp_checksum
    )

    return udp_header + message