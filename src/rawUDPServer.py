import socket
import os
from transport import unpack_udp_segment, create_udp_segment
from network import unpack_ip_packet, create_ip_packet
from util import get_server_dir, fragment_data


def send_file(server_socket, filename, client_ip, client_port):
    # Check if file exists
    if not os.path.isfile(os.path.join(get_server_dir(), filename)):
        http_response = "HTTP/1.1 404 Not Found\r\n\r\n"
        udp_segment = create_udp_segment(http_response.encode(), server_ip, server_port, client_ip, client_port)
        packet = create_ip_packet(server_ip, client_ip, udp_segment)
        server_socket.sendto(packet, (client_ip, client_port))
    else:
        with open(os.path.join(get_server_dir(), filename), 'rb') as f:
            content = f.read()
            to_send = fragment_data(content)
            # 202 for all packets except the last one
            for i, data in enumerate(to_send):
                if i != len(to_send) - 1:
                    http_response = "HTTP/1.1 202 OK\r\n\r\n".encode() + data
                else:
                    http_response = "HTTP/1.1 200 OK\r\n\r\n".encode() + data

                udp_segment = create_udp_segment(http_response, server_ip, server_port, client_ip, client_port)
                packet = create_ip_packet(server_ip, client_ip, udp_segment)
                server_socket.sendto(packet, (client_ip, client_port))


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 12345
    buffer_size = 65535

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    server_socket.bind((server_ip, server_port))
    print("Server started, waiting for request...")
    # gracefully handle keyboard interrupt
    try:
        while True:
            raw_data, addr = server_socket.recvfrom(buffer_size)
            ip_version, ip_header_length, ip_ttl, ip_protocol, ip_source_address, ip_destination_address, udp_segment = (
                unpack_ip_packet(raw_data))

            udp_source_port, udp_destination_port, udp_length, udp_checksum, payload = unpack_udp_segment(udp_segment)
            # Check if the destination port is the same as the server port
            if udp_destination_port == server_port:
                # Extract the HTTP request from the payload
                http_request = payload.decode()
                filename = http_request.split(' ')[1].strip('/')
                # Send the file or error response back to the client
                print("Received request for file: " + filename)
                send_file(server_socket, filename, ip_source_address, udp_source_port)
    except KeyboardInterrupt:
        print("Server interrupted by user, bye!")
