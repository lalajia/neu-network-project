# neu-network-project

CS5700 Foundation of Network

1. cd server
2. In terminal: sudo python3 rawUDPServer.py
3. cd client
4. In a new terminal: sudo python3 rawUDPClient.py

## Error from Server Side

### After

test1.txt
test2.txt
Enter the file name to download:
test1.txt
Received file saved as 'received_file'

### Server Response

Starting server on port: 12345
Received packet from: ('127.0.0.1', 0)
File: test1.txt
Traceback (most recent call last):
File "rawUDPServer.py", line 91, in <module>
with open(file_name, "rb") as file:
FileNotFoundError: [Errno 2] No such file or directory: ''
