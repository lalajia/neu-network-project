import socket
import struct
import udp_segment
import ip_datagram
import utils

if __name__ == "__main__":
    serverName = "127.0.0.1"  # Server IP
    clientName = "127.0.0.1" # Client IP
    serverPort = 12345  # Server Port Number
    clientPort = 54322 # Client Port Number
    server_addr = (
        serverName,
        serverPort,
    )  # Tuple to identify the UDP connection while sending


    print("Enter the file name to download:")

    message = input()
    user_data = message.encode()
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    # send the file name to server (it is wield that this is send to the client itself as well)
    utils.send_data(clientSocket, user_data, clientName, clientPort, serverName, serverPort)

    # client receives the packet from server 
    while True:
        message, source_ip, source_port= utils.receive_packet(clientSocket)
        print("message", message)
        print("source ip", source_ip)
        print("source port", source_port)
        # check if the soruce ip and port is same as server ip and port
        if source_ip == serverName and source_port == serverPort:
            # if yes, then the message is the file data, append it to the file
            with open("received_file.txt","ab") as file:
                file.write(message.encode() + b'\n')
                print("Received file saved as 'received_file'")
        



# received_data, serverAddress = clientSocket.recvfrom(2048)

# print(".....", received_data)
# # print("Received file data from server test......", received_data[48:])

# # # write the received file to disk
# # with open("received_file.txt", "wb") as file:
# #     byte, server = clientSocket.recvfrom(2048)
# #     file.write(byte[20:])
# #     print("Received file saved as 'received_file'")



# # # write the received file to disk
# # with open("received_file.txt","wb") as file:
# #     file.write(received_data)
# #     print("Received file saved as 'received_file'")

    clientSocket.close()


