import socket
import os
from util import get_server_dir, get_client_dir, fragment_data
from transport import unpack_udp_segment, create_udp_segment
from network import unpack_ip_packet, create_ip_packet


def create_http_request(filename_to_request):
    # define the http request header
    http_request_header = "GET /" + filename_to_request + " HTTP/1.1\r\n\r\n"
    return http_request_header.encode()

def send_ack(client_socket, server_ip, server_port, sequence_num):
    ack_data = f"ACK {sequence_num}".encode()
    ack_udp_segment = create_udp_segment(ack_data, client_ip, client_port, server_ip, server_port)
    ack_packet = create_ip_packet(client_ip, server_ip, ack_udp_segment)
    client_socket.sendto(ack_packet, (server_ip, server_port))


def receive_file(client_socket, server_ip, server_port, buffer_size=65535):
    expected_seq_num = 0  # This will be the next expected sequence number
    packet_buffer = {}  # Buffer for out-of-order packets

    print("Listening for incoming file data...")

    try:
        while True:
            raw_data, addr = client_socket.recvfrom(buffer_size)
            # Unpack IP and UDP headers
            ip_version, ip_header_length, ip_ttl, ip_protocol, ip_source_address, ip_destination_address, udp_segment \
                = unpack_ip_packet(raw_data)
            udp_source_port, udp_destination_port, udp_length, udp_checksum, payload = unpack_udp_segment(udp_segment)

            if ip_source_address == server_ip and udp_source_port == server_port:
                header_end = payload.find(b'\r\n\r\n')
                headers = payload[:header_end].decode('ascii', errors='ignore')
                body = payload[header_end + 4:]
                http_response_code = headers.split(" ")[1]

                # Handle different HTTP response codes
                if http_response_code == "404":
                    print("File not found on server.")
                    break
                elif http_response_code in ["200", "202"]:
                    # Extract the sequence number from the HTTP response
                    sequence_num = int(headers.split("Sequence: ")[1].split("\r\n")[0])
                    if sequence_num == expected_seq_num:
                        # Write the received data to file
                        print(f"Received packet {sequence_num}.")
                        with open(os.path.join(get_client_dir(), filename_to_request), "ab") as file:
                            file.write(body)

                        # Update the expected sequence number
                        expected_seq_num += 1

                        # Check the buffer for the next expected packet
                        while expected_seq_num in packet_buffer:
                            with open(os.path.join(get_client_dir(), filename_to_request), "ab") as file:
                                file.write(packet_buffer.pop(expected_seq_num))
                            expected_seq_num += 1

                        # Send ACK for the received sequence number
                        send_ack(client_socket, server_ip, server_port, sequence_num)

                        # If the response code is "200", it's the last packet
                        if http_response_code == "200":
                            print("File receive complete.")
                            break
                    else:
                        # Buffer out-of-order packets
                        if sequence_num > expected_seq_num:
                            packet_buffer[sequence_num] = body

                        # Resend ACK for the last in-order sequence number
                        send_ack(client_socket, server_ip, server_port, expected_seq_num - 1)
                else:
                    print("Error: Unknown HTTP response code.")
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

    receive_file(client_socket, server_ip, server_port)
    client_socket.close()
