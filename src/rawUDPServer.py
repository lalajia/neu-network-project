import os
import socket
import time
from sys import platform

from util import get_server_dir, fragment_data
from transport import create_udp_segment, unpack_udp_segment, udp_checksum_calc
from network import create_ip_packet, unpack_ip_packet

# Constants
TIMEOUT = 0.030  # Timeout interval in seconds
K = 10  # Window size

def extract_ack_number(ack_packet):
    try:
        message = unpack_udp_segment(unpack_ip_packet(ack_packet)[6])[4]
        return int(message.decode().split(" ")[1])
    except:
        return -1


def send_file(server_socket, filename, client_ip, client_port, server_ip, server_port):
    # Check if file exists
    if not os.path.isfile(os.path.join(get_server_dir(), filename)):
        http_response = "HTTP/1.1 404 Not Found\r\n\r\n"
        udp_segment = create_udp_segment(http_response.encode(), server_ip, server_port, client_ip, client_port)
        packet = create_ip_packet(server_ip, client_ip, udp_segment)
        server_socket.sendto(packet, (client_ip, client_port))
    else:
        with open(os.path.join(get_server_dir(), filename), "rb") as f:
            content = f.read()
            to_send = fragment_data(content)

            # Initialize sliding window parameters
            window_base = 0
            window_end = 0
            acked_sequence_numbers = set()
            server_socket.settimeout(TIMEOUT)  # Set the timeout for ACK

            while window_base < len(to_send):
                # Send packets within the window
                while window_end < window_base + K and window_end < len(to_send):
                    # Prepare and send the packet
                    response_code = "202 OK" if window_end < len(to_send) - 1 else "200 OK"
                    http_response = f"HTTP/1.1 {response_code}\r\nSequence: {window_end}\r\n\r\n".encode() + to_send[window_end]
                    udp_segment = create_udp_segment(http_response, server_ip, server_port, client_ip, client_port)
                    packet = create_ip_packet(server_ip, client_ip, udp_segment)
                    server_socket.sendto(packet, (client_ip, client_port))
                    window_end += 1

                try:
                    # Wait for an ACK
                    ack_packet, _ = server_socket.recvfrom(1024)
                    ack_num = extract_ack_number(ack_packet)
                    if ack_num >= 0:
                        acked_sequence_numbers.add(ack_num)
                        # Slide the window forward
                        while window_base in acked_sequence_numbers:
                            acked_sequence_numbers.remove(window_base)
                            window_base += 1
                except socket.timeout:
                    # Resend all packets in the window
                    for seq_num in range(window_base, window_end):
                        response_code = "202 OK" if seq_num < len(to_send) - 1 else "200 OK"
                        http_response = f"HTTP/1.1 {response_code}\r\nSequence: {seq_num}\r\n\r\n".encode() + to_send[seq_num]
                        udp_segment = create_udp_segment(http_response, server_ip, server_port, client_ip, client_port)
                        packet = create_ip_packet(server_ip, client_ip, udp_segment)
                        server_socket.sendto(packet, (client_ip, client_port))

            server_socket.settimeout(None)  # Reset the timeout


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
