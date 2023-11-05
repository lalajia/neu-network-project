import socket
from common import unpack_udp_segment, unpack_ip_packet, fragment_data, create_udp_segment, create_ip_packet

def create_http_request(filename_to_request):
    # use http request to request the file
    # define the http request header
    http_request_header = "GET /" + filename_to_request + " HTTP/1.1\r\n\r\n"
    return http_request_header.encode()

def receive_file(client_socket, buffer_size=65535):
    print("Listening for incoming file data...")
    try:
        while True:
            raw_data, addr = client_socket.recvfrom(buffer_size)
            if addr[0] == server_name and addr[1] == server_port:
                payload = unpack_udp_segment(unpack_ip_packet(raw_data)[6])[4]
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
                    with open(filename_to_save, "ab") as file:
                        file.write(body.encode())
                    break
                elif http_response_code == "202":
                    # file received in progress
                    with open(filename_to_save, "ab") as file:
                        file.write(body.encode())
                    continue
                else:
                    print("Error: Unknown http response code.")
                    break
    except KeyboardInterrupt:
        print("File reception interrupted by user.")

if __name__ == "__main__":
    ######### Choose the file to download #########
    print("Enter the file name to download:")
    # Print the list of files available
    print("test1.txt")
    print("test2.txt")
    filename_to_request = input()
    request = create_http_request(filename_to_request)
    to_send = fragment_data(request)
    filename_to_save = "download_"+filename_to_request
    ######### Connections ##########
    server_name = "127.0.0.1"  # Server IP
    client_name = "127.0.0.1"
    server_port = 12345  # Server Port Number
    client_port = 54321
    server_addr = (
        server_name,
        server_port
    )  # Tuple to identify the UDP connection while sending
    ################## UDP raw socket ###################
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    for payload in to_send:
        udp_segment = create_udp_segment(payload, client_name, client_port, server_name, server_port)
        packet = create_ip_packet(client_name, server_name, udp_segment)
        for i in range(100):
            client_socket.sendto(packet, (server_name, 0))

    receive_file(client_socket)
    client_socket.close()
