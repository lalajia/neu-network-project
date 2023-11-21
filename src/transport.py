import struct
import socket

# the pseudo header is used to calculate the checksum of udp segment, the length is the length of total udp segment
def upd_pseudo_header(source_ip, dest_ip, udp_length):
    # Convert IP addresses to packed binary format
    source_ip_packed = socket.inet_aton(source_ip)
    dest_ip_packed = socket.inet_aton(dest_ip)
    # Pack the pseudo-header
    pseudo_header = struct.pack("!4s4sBBH", source_ip_packed, dest_ip_packed, 0, 17, udp_length)
    return pseudo_header

# this function is used to calculate the checksum of udp segment in the sender side
def udp_checksum_calc(udp_segment, source_ip, dest_ip):
    # add the pseudo header
    udp_length = len(udp_segment) 
    udp_pseudo_header = upd_pseudo_header(source_ip, dest_ip, udp_length)
    udp_segment_temp = udp_pseudo_header + udp_segment
    # calculate the checksum
    checksum = 0
    # if the segment has odd number of bytes, add a 0 byte to the end
    if len(udp_segment_temp) % 2 == 1:
        udp_segment_temp += b'\x00'
    for i in range(0, len(udp_segment_temp), 2):
        #skip the checksum field
        if i == 6 + len(udp_pseudo_header):
            continue
        word = (udp_segment_temp[i] << 8) + udp_segment_temp[i + 1]
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    checksum = ~checksum & 0xffff
    return checksum



def create_udp_segment(payload, source_ip, source_port, dest_ip, dest_port):
    udp_total_length = len(payload) + 8 # 8 bytes for udp header
    udp_header_withoutchecksum = struct.pack("!HHHH", source_port, dest_port, udp_total_length, 0)
    udp_segment_withoutchecksum = udp_header_withoutchecksum + payload
    # calculate the checksum
    udp_checksum = udp_checksum_calc(udp_segment_withoutchecksum, source_ip, dest_ip)
    # print("test udp checksum calculated in the create: ", udp_checksum)
    # update the udp header with checksum
    udp_header = struct.pack("!HHHH", source_port, dest_port, udp_total_length, udp_checksum)
    return udp_header + payload


def unpack_udp_segment(udp_segment):
    udp_header = udp_segment[:8]
    udp_header = struct.unpack("!HHHH", udp_header)
    udp_source_port = udp_header[0]
    udp_destination_port = udp_header[1]
    udp_length = udp_header[2]
    udp_checksum = udp_header[3]
    payload = udp_segment[8:]
    return udp_source_port, udp_destination_port, udp_length, udp_checksum, payload


# this function is used to check the checksum of udp segment in the receiver side
def check_checksum(checksum, udp_segment, source_ip, dest_ip): # the source_ip and des_ip is string
    # create a pseudo header
    udp_length = len(udp_segment)
    udp_pseudo_header = upd_pseudo_header(source_ip, dest_ip, udp_length)
    udp_segment_temp = udp_pseudo_header + udp_segment
    # calculate the checksum
    checksum_received = udp_checksum_calc(udp_segment_temp, source_ip, dest_ip)
    if checksum_received == checksum:
        return True
    else:
        return False
