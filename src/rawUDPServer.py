import os
import socket
import time
from sys import platform

from util import get_server_dir, fragment_data
from transport import create_udp_segment, unpack_udp_segment, udp_checksum_calc
from network import create_ip_packet, unpack_ip_packet

# Constants
TIMEOUT = 0.025  # Timeout interval in seconds
K = 100  # Window size
debug = False

# Extracts the acknowledgment number from an acknowledgment packet. Used in the acknowledgment reception process to determine the acknowledged sequence number.
def extract_ack_number(ack_packet):
    try:
        message = unpack_udp_segment(unpack_ip_packet(ack_packet)[6])[4]
        return int(message.decode().split(" ")[1])
    except:
        return -1

# Checks whether a file with a given filename exists in the server directory. Used to handle cases where the requested file does not exist on the server.
def file_exists(filename):
    return os.path.isfile(os.path.join(get_server_dir(), filename))

# Prepares an HTTP response based on the sequence number, fragment, and total number of fragments. Used to construct HTTP responses with appropriate response codes.
def prepare_http_response(sequence_num, fragment, total_fragments):
    response_code = "202 OK" if sequence_num < total_fragments - 1 else "200 OK"
    return f"HTTP/1.1 {response_code}\r\nSequence: {sequence_num}\r\n\r\n".encode() + fragment

# Sends a UDP packet containing an HTTP response fragment to the client. Used to transmit file fragments to the client.
def send_packet(server_socket, sequence_num, fragment, server_ip, client_ip, server_port, client_port):
    http_response = prepare_http_response(sequence_num, fragment, len(fragmented_data))
    udp_segment = create_udp_segment(http_response, server_ip, server_port, client_ip, client_port)
    packet = create_ip_packet(server_ip, client_ip, udp_segment)
    server_socket.sendto(packet, (client_ip, client_port))

# Handles the reception of acknowledgment packets, updating the set of acknowledged sequence numbers. Used in the file transmission loop to handle acknowledgments.
def handle_ack_reception(server_socket, acked_sequence_numbers):
    try:
        ack_packet, _ = server_socket.recvfrom(1024)
        ack_num = extract_ack_number(ack_packet)
        return ack_num
    except socket.timeout:
        return None
    
# Handles the scenario where the requested file is not found, sending a 404 HTTP response. Used to notify the client that the requested file is not available.
def handle_file_not_found(server_socket, client_ip, client_port, server_ip, server_port):
    http_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    udp_segment = create_udp_segment(http_response.encode(), server_ip, server_port, client_ip, client_port)
    packet = create_ip_packet(server_ip, client_ip, udp_segment)
    server_socket.sendto(packet, (client_ip, client_port))
    return None

# Initiates the file transmission process by reading the file, fragmenting it, and sending fragments to the client. The main function responsible for sending the requested file to the client.
def send_file(server_socket, filename, client_ip, client_port, server_ip, server_port):
    if not file_exists(filename):
        return handle_file_not_found(server_socket, client_ip, client_port, server_ip, server_port)

    with open(os.path.join(get_server_dir(), filename), "rb") as f:
        content = f.read()
        global fragmented_data
        fragmented_data = fragment_data(content)

    window_base = 0
    window_end = 0
    acked_sequence_numbers = set()
    packet_sent_time = {}
    server_socket.settimeout(TIMEOUT)
    while window_base < len(fragmented_data):
        # queue up packets to send
        while window_end < window_base + K and window_end < len(fragmented_data):
            if window_end not in acked_sequence_numbers:
                if debug:
                    print("sending", window_end)
                send_packet(server_socket, window_end, fragmented_data[window_end], server_ip, client_ip, server_port, client_port)
                packet_sent_time[window_end] = time.time()
            window_end += 1

        ack_num = handle_ack_reception(server_socket, acked_sequence_numbers)
        if ack_num is not None and 0 <= ack_num < len(fragmented_data):
            if debug:
                print("received ack", ack_num)
            acked_sequence_numbers.add(ack_num)
            while window_base in acked_sequence_numbers:
                acked_sequence_numbers.remove(window_base)
                window_base += 1

        current_time = time.time()
        for seq_num in range(window_base, window_end):
            if seq_num not in acked_sequence_numbers and current_time - packet_sent_time.get(seq_num, 0) > TIMEOUT:
                if debug:
                    print("time out", seq_num)
                send_packet(server_socket, seq_num, fragmented_data[seq_num], server_ip, client_ip, server_port, client_port)
                packet_sent_time[seq_num] = current_time
    server_socket.settimeout(None)





if __name__ == "__main__":
    # server_ip = "127.0.0.1"
    server_ip = "192.168.1.5" # mininet
    # client_ip = "192.168.1.7" # mininet2
    server_port = 12345
    buffer_size = 65535

    if platform == "darwin":
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        #server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    server_socket.bind(("0.0.0.0", server_port))
    print("Server started, waiting for request...")
    # gracefully handle keyboard interrupt
    try:
        while True:
            raw_data, addr = server_socket.recvfrom(buffer_size)
            (
                ip_version,
                ip_header_length,
                ip_ttl,
                ip_protocol,
                ip_source_address,
                ip_destination_address,
                udp_segment,
            ) = unpack_ip_packet(raw_data)
            (
                udp_source_port,
                udp_destination_port,
                udp_length,
                udp_checksum,
                payload,
            ) = unpack_udp_segment(udp_segment)
            # Check if the destination port is the same as the server port
            if ip_protocol == socket.IPPROTO_UDP and udp_destination_port == server_port:
                # check the udp checksum
                checksum_received = udp_checksum_calc(udp_segment, ip_source_address, ip_destination_address)
                if checksum_received != udp_checksum:
                    print("UDP checksum mismatch, discard.")
                    continue
                # Extract the HTTP request from the payload
                http_request = payload.decode()
                filename = http_request.split(" ")[1].strip("/")
                # Send the file or error response back to the client
                print("Received request for file: " + filename)

                send_file(
                    server_socket,
                    filename,
                    ip_source_address,
                    udp_source_port,
                    server_ip,
                    server_port,
                )
    except KeyboardInterrupt:
        print("Server interrupted by user, bye!")
