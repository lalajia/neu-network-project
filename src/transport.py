import struct


def udp_checksum(udp_datagram, source_ip, dest_ip, udp_total_length):
    def one_s_complement(msg):
        # TODO: implement one's complement
        return 0

    # TODO: implement the checksum
    # calculate pseudo header,pass to one's complement together with udp_datagram
    return 0


def create_udp_segment(payload, source_ip, source_port, dest_ip, dest_port):
    udp_length = len(payload) + 8
    udp_psudoheader = struct.pack("!HHHH", source_port, dest_port, udp_length, 0)
    udp_datagram = udp_psudoheader + payload
    checksum = udp_checksum(udp_datagram, source_ip, dest_ip, udp_length)
    udp_header = struct.pack("!HHHH", source_port, dest_port, udp_length, checksum)
    return udp_header + payload


def unpack_udp_segment(udp_segment):
    udp_header = udp_segment[:8]
    udp_header = struct.unpack("!HHHH", udp_header)
    udp_source_port = udp_header[0]
    udp_destination_port = udp_header[1]
    udp_length = udp_header[2]
    udp_checksum = udp_header[3]
    payload = udp_segment[28:]
    # something = udp_segment[8:28]
    # print("somthing is: ", something.decode())
    # print("udp_header is: ", udp_header)
    # print("udp_source_port is: ", udp_source_port)
    # print("udp_destination_port is: ", udp_destination_port)
    # print("payload is: ", payload)
    return udp_source_port, udp_destination_port, udp_length, udp_checksum, payload
