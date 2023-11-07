import socket
import struct
import ip_datagram
import udp_segment
import utils    


# def receive_packet(rawSocket):
#     packet, addr = rawSocket.recvfrom(65535)
#     # Parse the packet (20 bytes for IP header and 8 bytes for UDP header)
#     ip_header = packet[20:40]
#     udp_header = packet[40:48]
#     payload = packet[48:]
    
#     # Unpack the IP header and UDP header
#     print("type of ip header", type(ip_header))
#     ip_header_data = struct.unpack("!BBHHHBBH4s4s", ip_header)
#     udp_header_data = struct.unpack("!HHHH", udp_header)
    
#     # Extract data from the headers
#     source_ip = socket.inet_ntoa(ip_header_data[8])
#     source_port = udp_header_data[0]
#     message = payload.decode("utf-8")
    
#     print(f"Received message from {source_ip}:{source_port}: {message}")
#     return message, source_ip, source_port

# def send_data(socket, payload, source_ip, source_port, destination_ip, destination_port):
#     segment = udp_segment.create_udp_segment(source_port, destination_port, payload)
#     datagram = ip_datagram.create_ip_datagram(source_ip, destination_ip, segment)
#     socket.sendto(datagram, (destination_ip, destination_port))




if __name__ == "__main__":
    serverName = "127.0.0.1"  # Server IP
    clientName = "127.0.0.1" # Client IP
    serverPort = 12345  # Server Port Number
    clientPort = 54322 # Client Port Number
    server_addr = (
        serverName,
        serverPort,
    )   
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    server_socket.bind(server_addr)
    print("Starting server on port:", serverPort)

    while True:
        message, source_ip, source_port= utils.receive_packet(server_socket)
        print("message", message)
        print("source ip", source_ip)
        print("source port", source_port)
        # check if the soruce ip and port is same as client ip and port
        if source_ip == clientName and source_port == clientPort:
            # if yes, then the message is the file name, read the file and send it to the client
            filename = message
            file_data = utils.readFile(filename)
            # this send to the server itself as well 
            utils.send_data(server_socket, file_data, serverName, serverPort, source_ip, source_port)
