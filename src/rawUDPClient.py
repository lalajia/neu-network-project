import socket
import os
from util import get_server_dir, get_client_dir, fragment_data
from transport import unpack_udp_segment, create_udp_segment
from network import unpack_ip_packet, create_ip_packet


def create_http_request(filename_to_request):
    # define the http request header
    http_request_header = "GET /" + filename_to_request + " HTTP/1.1\r\n\r\n"
    return http_request_header.encode()


def receive_file(client_socket, buffer_size=65535):
    print("Listening for incoming file data...")
    try:
        while True:
            raw_data, addr = client_socket.recvfrom(buffer_size)
            ip_version, ip_header_length, ip_ttl, ip_protocol, ip_source_address, ip_destination_address, udp_segment \
                = unpack_ip_packet(raw_data)
            udp_source_port, udp_destination_port, udp_length, udp_checksum, payload = unpack_udp_segment(udp_segment)
            if ip_source_address == server_ip and udp_source_port == server_port:
                header_end = payload.find(b'\r\n\r\n')
                headers = payload[:header_end].decode('ascii', errors='ignore')
                body = payload[header_end + 4:]
                # get http response code
                http_response_code = headers.split(" ")[1]
                if http_response_code == "404":
                    print("File not found on server.")
                    break
                elif http_response_code == "200":
                    print("File receive complete.")
                    with open(os.path.join(get_client_dir(), filename_to_request), "ab") as file:
                        file.write(body)
                    break
                elif http_response_code == "202":
                    print("File receive in progress...")
                    with open(os.path.join(get_client_dir(), filename_to_request), "ab") as file:
                        file.write(body)
                    continue
                else:
                    print("Error: Unknown http response code.")
                    break
    except KeyboardInterrupt:
        print("File reception interrupted by user.")


if __name__ == "__main__":
    ######### Choose the file to download #########
    print("Enter the file name to download:")
    # print a list of files available to server
    files_in_resources = os.listdir(get_server_dir())
    print("\n".join(files_in_resources))
    filename_to_request = input()
    request = create_http_request(filename_to_request)
    to_send = fragment_data(request)
    # check if file exists in download directory
    if filename_to_request in os.listdir(get_client_dir()):
        # if so remove it
        os.remove(os.path.join(get_client_dir(), filename_to_request))
        print("File already exists in download directory, overriding...")
    ######### Connections ##########

    server_ip = "127.0.0.1"
    client_ip = "127.0.0.1"
    server_port = 12345  # Server Port Number
    client_port = 54321
    server_addr = (
        server_ip,
        server_port
    )  # Tuple to identify the UDP connection while sending
    ################## UDP raw socket ###################
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    # tell kernel not to put in headers, since we are providing it
    client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    client_socket.bind((client_ip, client_port))
    for payload in to_send:
        udp_segment = create_udp_segment(payload, client_ip, client_port, server_ip, server_port)
        packet = create_ip_packet(client_ip, server_ip, udp_segment)
        client_socket.sendto(packet, server_addr)

    receive_file(client_socket)
    client_socket.close()
