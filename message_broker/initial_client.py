import socket
import sys
import json

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 7070)
print('Connecting to {addr} port {port} '.format(addr=server_address[0], port=server_address[1]))
sock.connect(server_address)
try:

    # Send data
    for i in [1,2,3]:
        message = json.dumps({
                    "name": "handshake",
                    "message_format": "xml",
                    "port": 777,
                    "message_type": "weather"
                    })
        sock.sendall(message.encode())
        # Look for the response
        data = sock.recv(1024)
        print('Response:\n' + data.decode() + '\n')

finally:
    print('Closing socket')
    sock.close()
